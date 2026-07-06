from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.services.search_service import search_content
from app.services.search.client import get_es_client

router = APIRouter(prefix="/search", tags=["search"])
logger = logging.getLogger("argus_api")


@router.get("")
async def search(
    q: str = Query(..., min_length=1, max_length=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Perform a hybrid search across all indexed content."""
    try:
        return await search_content(q, db)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        # Return empty results if Elasticsearch is unavailable
        return {"q": q, "results": []}
