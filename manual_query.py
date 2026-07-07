import asyncio, os, sys
import httpx
sys.path.append(os.path.abspath('backend'))
from app.services.search.client import settings, INDEX_NAME

async def main():
    async with httpx.AsyncClient() as client:
        # BM25 query for planetary
        query = {
            "size": 10,
            "query": {"match": {"content": {"query": "planetary", "operator": "and"}}}
        }
        resp = await client.post(f"{settings.ELASTICSEARCH_URL}/{INDEX_NAME}/_search", json=query)
        print('Status', resp.status_code)
        print('Response', resp.json())

if __name__ == '__main__':
    asyncio.run(main())
