from __future__ import annotations

from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

# Import the new Elasticsearch client utilities.
from app.services.search.client import get_es_client, init_index, hybrid_search


async def search_content(q: str, db: AsyncSession) -> dict[str, Any]:
    """Perform a hybrid BM25 + vector search using Elasticsearch.

    The ``db`` argument is retained for compatibility with existing route
    signatures, but is not used by the current implementation.
    """
    # Ensure the Elasticsearch client is ready and the index exists.
    es = await get_es_client()
    await init_index(es)

    # Execute the hybrid search – it returns a list of document dicts.
    results = await hybrid_search(es, q)
    return {"q": q, "results": results}
