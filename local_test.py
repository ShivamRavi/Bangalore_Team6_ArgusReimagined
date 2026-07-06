import asyncio, json
import httpx, sys, os
from httpx import AsyncClient, ASGITransport
sys.path.append(os.path.abspath('backend'))
from app.main import app

async def run():
    async with httpx.AsyncClient(app=app, base_url='http://test') as client:
        # health
        r = await client.get('/healthz')
        print('Health', r.status_code, r.json())
        # register staff
        payload = {'username': 'testuser2', 'password': 'testpass2', 'role': 'STAFF'}
        r = await client.post('/api/v1/auth/register', json=payload)
        print('Register', r.status_code, r.text)
        if r.is_success:
            print('Token', r.json())
        else:
            # try to get detailed error if any
            pass

asyncio.run(run())
