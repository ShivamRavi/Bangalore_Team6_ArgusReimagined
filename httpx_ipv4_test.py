import asyncio, httpx, sys, os, traceback
async def main():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get('http://127.0.0.1:9200', timeout=5.0)
            print('Status', r.status_code)
            print('Body', r.text[:200])
    except Exception as e:
        print('Error', e)
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
