from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.services.search_service import search_content
from app.services.search.client import get_es_client, init_index, settings, INDEX_NAME

router = APIRouter(prefix="/search", tags=["search"])
logger = logging.getLogger("argus_api")


@router.get("")
async def search(
    q: str = Query(..., min_length=1, max_length=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Perform a hybrid search across all indexed content."""
    # Ensure Elasticsearch index exists
    await init_index(await get_es_client())
    # Perform a simple BM25 search using HTTP client
    import httpx
    bm25_body = {"size": 10, "query": {"match": {"content": {"query": q, "operator": "and"}}}}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{settings.ELASTICSEARCH_URL}/{INDEX_NAME}/_search", json=bm25_body)
        resp_json = resp.json()
        logger.info(f"ES BM25 response: {resp_json}")
        hits = resp_json.get("hits", {}).get("hits", [])
        results = [hit["_source"] | {"_id": hit["_id"]} for hit in hits]
    return {"q": q, "results": results}
