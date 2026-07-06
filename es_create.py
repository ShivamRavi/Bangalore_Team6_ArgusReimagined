import asyncio, sys, os
sys.path.append(os.path.abspath('backend'))
from app.services.search.client import get_es_client, init_index

async def main():
    es = await get_es_client()
    try:
        await init_index(es)
        print('Index created or already exists')
    except Exception as e:
        print('Error creating index', e)

if __name__ == '__main__':
    asyncio.run(main())
