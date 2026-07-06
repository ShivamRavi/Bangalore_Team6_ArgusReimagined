import asyncio, sys, os
sys.path.append(os.path.abspath('backend'))
from app.services.search.client import get_es_client, INDEX_NAME

async def main():
    es = await get_es_client()
    exists = await es.indices.exists(index=INDEX_NAME)
    print('Exists returned', exists)
    # Also try HEAD manually via httpx
    import httpx
    async with httpx.AsyncClient() as client:
        resp = await client.head(f'http://127.0.0.1:9200/{INDEX_NAME}')
        print('HTTPX HEAD status', resp.status_code)

if __name__ == '__main__':
    asyncio.run(main())
