import asyncio
import httpx
import os
import sys
import uuid

# Ensure the backend package is on the import path
sys.path.append(os.path.abspath('backend'))

from app.services.search.client import get_es_client, init_index, index_document, INDEX_NAME


async def main():
    async with httpx.AsyncClient(base_url='http://127.0.0.1:8000') as client:
        # Register a new user for the test
        username = f"search_user_{uuid.uuid4().hex[:8]}"
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "password": "testpass",
                "role": "STUDENT",
                "house_id": 1,
                "section_id": 1,
            },
        )
        print('Register response:', reg_resp.status_code, reg_resp.text)
        if reg_resp.status_code != 201:
            return
        token = reg_resp.json()["access_token"]

        # Index a document directly into Elasticsearch
        es = await get_es_client()
        await init_index(es)
        doc = {
            "title": "Planetary Exploration",
            "content": "This is about planetary science and space travel.",
        }
        await index_document(es, doc)
        await es.indices.refresh(index=INDEX_NAME)

        # Perform a search query
        search_resp = await client.get(
            "/api/v1/search",
            params={"q": "planetary"},
            headers={"Authorization": f"Bearer {token}"},
        )
        print('Search response status:', search_resp.status_code)
        print('Search response body:', search_resp.json())

if __name__ == "__main__":
    asyncio.run(main())
