import asyncio, os, sys
import httpx
sys.path.append(os.path.abspath('backend'))
from app.services.search.client import get_es_client, init_index, index_document, hybrid_search, INDEX_NAME, settings

async def main():
    es = await get_es_client()
    # delete index if exists
    try:
        await es.indices.delete(index=INDEX_NAME)
    except Exception as e:
        print('Delete error ignored:', e)
    await init_index(es)
    doc = {"title": "Planetary Exploration", "content": "Content about planetary science and space travel."}
    # Index document manually for debugging
    async with httpx.AsyncClient() as client:
        post_resp = await client.post(f"{settings.ELASTICSEARCH_URL}/{INDEX_NAME}/_doc", json=doc)
        print('Manual index status', post_resp.status_code)
    # Use existing index_document function as well (should be same)
    await index_document(es, doc)
    # refresh using patched method
    await es.indices.refresh(index=INDEX_NAME)
    # Verify that document is present via match_all query
    async with httpx.AsyncClient() as client:
        resp_all = await client.post(f"{settings.ELASTICSEARCH_URL}/{INDEX_NAME}/_search", json={"query": {"match_all": {}}})
        print('Match_all response', resp_all.json())
    results = await hybrid_search(es, "planetary")
    print('Hybrid search results:', results)

if __name__ == '__main__':
    asyncio.run(main())
