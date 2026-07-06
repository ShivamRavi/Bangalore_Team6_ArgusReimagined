import asyncio, json, httpx, traceback, sys, os

async def main():
    url = 'http://127.0.0.1:9200/argus_knowledge'
    mapping = {
        "mappings": {
            "properties": {
                "data_type": {"type": "keyword"},
                "text_vector": {
                    "type": "dense_vector",
                    "dims": 384,
                    # "index": True,  # remove invalid param
                    "similarity": "cosine"
                },
                "username": {"type": "keyword"},
                "email": {"type": "keyword"},
                "title": {"type": "text"},
                "content": {"type": "text"},
                "start_time": {"type": "date"},
                "end_time": {"type": "date"}
            }
        }
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.put(url, json=mapping, timeout=10.0)
            print('PUT status', resp.status_code)
            print('Response', resp.text)
        except Exception as e:
            print('Error', e)
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
