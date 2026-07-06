"""Script to index Argus content into Elasticsearch.

Run this script after starting the Elasticsearch container (docker-compose up -d).
It uses the async Elasticsearch client defined in ``backend/app/services/search/client.py``.
"""

import asyncio
from typing import List, Dict, Any

# Import the client utilities
from ..services.search.client import get_es_client, init_index, index_document

# Example documents – in a real scenario, replace with data from the database or files.
SAMPLE_DOCS: List[Dict[str, Any]] = [
    {
        "id": "worksheet-1",
        "title": "Planetary Math Worksheet",
        "description": "Practice core math concepts related to planets and space.",
        "type": "worksheet",
        "content": "... full text of worksheet ...",
    },
    {
        "id": "quiz-1",
        "title": "Stellar Quiz",
        "description": "Reinforce your understanding with a quick quiz.",
        "type": "quiz",
        "content": "... quiz questions and answers ...",
    },
    {
        "id": "video-1",
        "title": "Mission Briefing Video",
        "description": "Watch a short lesson and earn your reward.",
        "type": "video",
        "content": "... transcript or summary ...",
    },
]


async def main() -> None:
    es = await get_es_client()
    await init_index(es)
    for doc in SAMPLE_DOCS:
        await index_document(es, doc)
    print(f"Indexed {len(SAMPLE_DOCS)} documents.")

if __name__ == "__main__":
    asyncio.run(main())
