import asyncio, os, sys
import httpx
sys.path.append(os.path.abspath('backend'))
from app.services.search.client import settings, INDEX_NAME

async def main():
    async with httpx.AsyncClient() as client:
        # Delete index if exists (ignore errors)
        try:
            await client.delete(f"{settings.ELASTICSEARCH_URL}/{INDEX_NAME}")
        except Exception as e:
            print('Delete error (ignored):', e)
        # Create index
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
        resp = await client.put(f"{settings.ELASTICSEARCH_URL}/{INDEX_NAME}", json=mapping)
        print('Create index status', resp.status_code)
        # Index a document
        doc = {"title": "Planetary Exploration", "content": "Content about planetary science and space travel."}
        resp = await client.post(f"{settings.ELASTICSEARCH_URL}/{INDEX_NAME}/_doc", json=doc)
        print('Index doc status', resp.status_code)
        # Refresh
        resp = await client.post(f"{settings.ELASTICSEARCH_URL}/{INDEX_NAME}/_refresh")
        print('Refresh status', resp.status_code)
        # Search BM25
        query = {
            "size": 10,
            "query": {"match": {"content": {"query": "planetary", "operator": "and"}}}
        }
        resp = await client.post(f"{settings.ELASTICSEARCH_URL}/{INDEX_NAME}/_search", json=query)
        print('Search status', resp.status_code)
        print('Search response', resp.json())

if __name__ == '__main__':
    asyncio.run(main())
