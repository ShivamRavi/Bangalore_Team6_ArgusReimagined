import asyncio, httpx, sys, os, traceback
sys.path.append(os.path.abspath('backend'))

async def main():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get('http://[::1]:9200', timeout=5.0)
            print('Status', resp.status_code)
            print('Text', resp.text[:200])
    except Exception as e:
        print('Error:', e)
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
