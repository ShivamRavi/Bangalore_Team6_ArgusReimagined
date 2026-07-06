import asyncio, httpx, traceback

async def main():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.head('http://127.0.0.1:9200/argus_knowledge')
            print('HEAD status', r.status_code)
            print('Headers', r.headers)
    except Exception as e:
        print('Error', e)
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
