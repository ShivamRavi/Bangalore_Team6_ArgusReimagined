import asyncio, os, sys
sys.path.append(os.path.abspath('backend'))
from app.services.search.client import get_es_client, INDEX_NAME

async def main():
    try:
        es = await get_es_client()
        exists = await es.indices.exists(index=INDEX_NAME)
        print('Exists:', exists)
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    asyncio.run(main())
