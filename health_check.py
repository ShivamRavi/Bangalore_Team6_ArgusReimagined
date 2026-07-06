import asyncio, httpx, os, sys
sys.path.append(os.path.abspath('backend'))

async def main():
    async with httpx.AsyncClient(base_url='http://127.0.0.1:8000') as client:
        resp = await client.get('/healthz')
        print('Status:', resp.status_code)
        try:
            print('JSON:', resp.json())
        except Exception:
            print('Text:', resp.text)

if __name__ == '__main__':
    asyncio.run(main())
