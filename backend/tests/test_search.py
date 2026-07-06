import pytest
from httpx import AsyncClient

from app.services.search.client import get_es_client, init_index, index_document, INDEX_NAME


@pytest.mark.asyncio
async def test_search_endpoint(client: AsyncClient):
    """End‑to‑end test for the /api/v1/search endpoint.

    It registers a user, indexes a test document directly into Elasticsearch,
    then performs a search query and verifies that the document is returned.
    """
    # Register a test user
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "search_user",
            "password": "searchpass",
            "role": "STUDENT",
            "house_id": 1,
            "section_id": 1,
        },
    )
    assert register_resp.status_code == 201
    token = register_resp.json()["access_token"]

    # Prepare Elasticsearch: delete index if it already exists, then recreate it
    es = await get_es_client()
    try:
        await es.indices.delete(index=INDEX_NAME)
    except Exception:
        # Index may not exist – ignore the error
        pass
    await init_index(es)

    # Index a single document containing the term "planetary"
    doc = {
        "title": "Planetary Exploration",
        "content": "Content about planetary science and space travel.",
    }
    await index_document(es, doc)
    # Ensure the document is searchable immediately
    await es.indices.refresh(index=INDEX_NAME)

    # Perform the search request
    response = await client.get(
        "/api/v1/search",
        params={"q": "planetary"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["q"] == "planetary"
    assert isinstance(data["results"], list)
    # At least one result should be returned
    assert len(data["results"]) > 0
    # Verify that our indexed document appears in the results
    titles = [r.get("title", "").lower() for r in data["results"]]
    assert any("planetary exploration" in t for t in titles)
