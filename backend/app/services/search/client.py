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
        _es_client = AsyncElasticsearch([settings.ELASTICSEARCH_URL])
    return _es_client


# ---------------------------------------------------------------------------
# Index management
# ---------------------------------------------------------------------------

INDEX_NAME = "argus_knowledge"


async def init_index(es: AsyncElasticsearch) -> None:
    """Create the ``argus_knowledge`` index if it does not already exist.

    The mapping mirrors the specification from the Phase 7 design:

    * ``data_type`` – keyword to identify the source (e.g. ``worksheet``).
    * ``text_vector`` – ``dense_vector`` with 384 dimensions (the size of the
      ``all-MiniLM-L6-v2`` embeddings).
    * ``username`` / ``email`` – keyword fields for user identification.
    * ``title`` / ``content`` – full‑text searchable fields.
    * ``start_time`` / ``end_time`` – optional date fields.
    """
    exists = await es.indices.exists(index=INDEX_NAME)
    if exists:
        return

    mapping: Dict[str, Any] = {
        "mappings": {
            "properties": {
                "data_type": {"type": "keyword"},
                "text_vector": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True,
                    "similarity": "cosine",
                },
                "username": {"type": "keyword"},
                "email": {"type": "keyword"},
                "title": {"type": "text"},
                "content": {"type": "text"},
                "start_time": {"type": "date"},
                "end_time": {"type": "date"},
            }
        }
    }
    await es.indices.create(index=INDEX_NAME, body=mapping)


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
    vector = _EMBEDDER.encode(text).tolist()
    body = {**doc, "text_vector": vector}
    await es.index(index=INDEX_NAME, document=body)


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
    query_vec = _EMBEDDER.encode(query).tolist()

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

    bm25_resp = await es.search(index=INDEX_NAME, body=bm25_body)
    knn_resp = await es.search(index=INDEX_NAME, body=knn_body)

    # Helper to map hit id to source.
    def collect_hits(resp: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [hit["_source"] | {"_id": hit["_id"]} for hit in resp["hits"]["hits"]]

    bm25_hits = collect_hits(bm25_resp)
    knn_hits = collect_hits(knn_resp)

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
