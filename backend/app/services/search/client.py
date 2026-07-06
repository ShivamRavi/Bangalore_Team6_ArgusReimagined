"""Elasticsearch async client and hybrid search utilities for Argus search.

This module provides:
* ``get_es_client`` – returns a shared :class:`AsyncElasticsearch` instance.
* ``init_index`` – creates the ``argus_knowledge`` index with the required mapping
  (including a ``dense_vector`` field for embeddings).
* ``index_document`` – indexes a single document after generating its embedding
  using the ``sentence-transformers`` model ``all-MiniLM-L6-v2``.
* ``hybrid_search`` – performs a BM25 text search and a k‑NN vector search, then
  merges the results using Reciprocal Rank Fusion (RRF).

The implementation is deliberately lightweight and async so it can be used
directly from FastAPI route handlers.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
import httpx
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

# Load configuration – the project already defines ``ELASTICSEARCH_URL`` in
# ``backend/app/config.py``. Importing the settings module ensures we respect any
# environment overrides the user may have configured.
# The config module lives one level higher (backend/app/config.py). Using a
# relative import with three dots correctly resolves the package hierarchy.
from ...config import settings

# Initialise the embedding model once – it is thread‑safe for inference.
if SentenceTransformer:
    _EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")
else:
    class _DummyEmbedder:
        def encode(self, text):
            return [0.0] * 384
    _EMBEDDER = _DummyEmbedder()

# ---------------------------------------------------------------------------
# Elasticsearch client handling
# ---------------------------------------------------------------------------

_es_client: AsyncElasticsearch | None = None


async def get_es_client() -> AsyncElasticsearch:
    """Return a singleton ``AsyncElasticsearch`` client.

    The client is created lazily on first use and re‑used for subsequent calls.
    ``settings.ELASTICSEARCH_URL`` is expected to be something like
    ``http://localhost:9200``.
    """
    global _es_client
    if _es_client is None:
        _es_client = AsyncElasticsearch([settings.ELASTICSEARCH_URL], headers={"Accept": "application/json", "Content-Type": "application/json"})
        # Monkey‑patch problematic methods to use plain HTTP requests without ES client compatibility headers.
        async def _safe_refresh(index: str, **kwargs):
            async with httpx.AsyncClient() as client:
                await client.post(f"{settings.ELASTICSEARCH_URL}/{index}/_refresh")
        async def _safe_delete(index: str, **kwargs):
            async with httpx.AsyncClient() as client:
                await client.delete(f"{settings.ELASTICSEARCH_URL}/{index}")
        # Assign the patched coroutines to the indices namespace.
        _es_client.indices.refresh = _safe_refresh
        _es_client.indices.delete = _safe_delete
    return _es_client


# ---------------------------------------------------------------------------
# Index management
# ---------------------------------------------------------------------------

INDEX_NAME = "argus_knowledge"


async def init_index(es: AsyncElasticsearch) -> None:
    """Create the ``argus_knowledge`` index if it does not already exist."""
    # Use HTTP client directly to avoid compatibility issues with the official client.
    async with httpx.AsyncClient() as client:
        # Check if index exists via HEAD request
        head_resp = await client.head(f"{settings.ELASTICSEARCH_URL}/{INDEX_NAME}")
        if head_resp.status_code == 200:
            return
        # Define mapping (same as before, without the invalid "index" field)
        mapping = {
            "mappings": {
                "properties": {
                    "data_type": {"type": "keyword"},
                    "text_vector": {"type": "dense_vector", "dims": 384, "similarity": "cosine"},
                    "username": {"type": "keyword"},
                    "email": {"type": "keyword"},
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "start_time": {"type": "date"},
                    "end_time": {"type": "date"},
                }
            }
        }
        # Create the index via PUT request
        await client.put(f"{settings.ELASTICSEARCH_URL}/{INDEX_NAME}", json=mapping)



# ---------------------------------------------------------------------------
# Document indexing
# ---------------------------------------------------------------------------

async def index_document(es: AsyncElasticsearch, doc: Dict[str, Any]) -> None:
    """Index a single document after adding its embedding.

    ``doc`` should contain a ``content`` (or ``text``) field that will be fed to
    the embedding model. The resulting vector is stored in ``text_vector``.
    """
    # Determine the text to embed – fall back to an empty string if missing.
    text = doc.get("content") or doc.get("text") or ""
    vector = _EMBEDDER.encode(text)
    if hasattr(vector, "tolist"):
        vector = vector.tolist()
    else:
        vector = list(vector)
    body = {**doc, "text_vector": vector}
    # Index document via HTTP request directly
    async with httpx.AsyncClient() as client:
        await client.post(f"{settings.ELASTICSEARCH_URL}/{INDEX_NAME}/_doc", json=body)


# ---------------------------------------------------------------------------
# Hybrid search implementation
# ---------------------------------------------------------------------------

async def hybrid_search(es: AsyncElasticsearch, query: str, k: int = 10) -> List[Dict[str, Any]]:
    """Perform BM25 + k‑NN search and merge results with Reciprocal Rank Fusion.

    The function executes two separate searches:
    1. A classic ``match`` query (BM25) on the ``content`` field.
    2. A ``knn`` query on the ``text_vector`` field using the query embedding.

    Results are combined in‑memory using RRF with ``k=60`` (a common default).
    The final list is sorted by the fused score and truncated to ``k`` items.
    """
    # Encode the query once.
    query_vec = _EMBEDDER.encode(query)
    if hasattr(query_vec, "tolist"):
        query_vec = query_vec.tolist()
    else:
        query_vec = list(query_vec)

    bm25_body = {
        "size": k,
        "query": {
            "match": {
                "content": {
                    "query": query,
                    "operator": "and",
                }
            }
        },
    }

    knn_body = {
        "size": k,
        "knn": {
            "field": "text_vector",
            "query_vector": query_vec,
            "k": k,
        "num_candidates": max(100, k * 10),
    },
}
    # Helper to map hit id to source.
    def collect_hits(resp: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [hit["_source"] | {"_id": hit["_id"]} for hit in resp["hits"]["hits"]]

    # Perform BM25 search
    async with httpx.AsyncClient() as client:
        bm25_resp = await client.post(f"{settings.ELASTICSEARCH_URL}/{INDEX_NAME}/_search", json=bm25_body)
    bm25_json = bm25_resp.json()
    bm25_hits = collect_hits(bm25_json)
    # Attempt KNN search (may not be supported); ignore failures.
    try:
        async with httpx.AsyncClient() as client:
            knn_resp = await client.post(f"{settings.ELASTICSEARCH_URL}/{INDEX_NAME}/_search", json=knn_body)
        knn_json = knn_resp.json()
        knn_hits = collect_hits(knn_json)
    except Exception:
        knn_hits = []

    # Apply Reciprocal Rank Fusion.
    rrf_k = 60.0
    scores: Dict[str, float] = {}
    for rank, hit in enumerate(bm25_hits, start=1):
        scores[hit["_id"]] = scores.get(hit["_id"], 0.0) + 1.0 / (rank + rrf_k)
    for rank, hit in enumerate(knn_hits, start=1):
        scores[hit["_id"]] = scores.get(hit["_id"], 0.0) + 1.0 / (rank + rrf_k)

    # Merge source dictionaries – prefer BM25 source when both exist.
    source_by_id: Dict[str, Dict[str, Any]] = {hit["_id"]: hit for hit in bm25_hits}
    for hit in knn_hits:
        source_by_id.setdefault(hit["_id"], hit)

    # Sort by fused score.
    sorted_ids = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:k]
    merged_results: List[Dict[str, Any]] = []
    for doc_id, fused_score in sorted_ids:
        src = source_by_id[doc_id].copy()
        src["_id"] = doc_id
        src["score"] = fused_score
        merged_results.append(src)

    return merged_results
