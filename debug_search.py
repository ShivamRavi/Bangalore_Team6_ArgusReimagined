import asyncio, os, sys
sys.path.append(os.path.abspath('backend'))
from app.services.search.client import get_es_client, init_index, index_document, hybrid_search, INDEX_NAME

async def main():
    es = await get_es_client()
    # delete index if exists
    try:
        await es.indices.delete(index=INDEX_NAME)
    except Exception as e:
        print('Delete error (ignore):', e)
    await init_index(es)
    # index doc
    doc = {"title": "Planetary Exploration", "content": "Content about planetary science and space travel."}
    await index_document(es, doc)
    await es.indices.refresh(index=INDEX_NAME)
    # perform search
    results = await hybrid_search(es, "planetary")
    print('Search results:', results)

if __name__ == '__main__':
    asyncio.run(main())
