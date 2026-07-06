import asyncio, json, os, sys
import httpx
sys.path.append(os.path.abspath('backend'))
from app.main import app

async def health_check(client):
    r = await client.get('/healthz')
    print('Health:', r.json())

async def register_user(client, username='testuser', password='testpass'):
    payload = {'username': username, 'password': password, 'role': 'STAFF'}
    r = await client.post('/api/v1/auth/register', json=payload)
    print('Register status:', r.status_code, r.text)
    return r.json()['access_token']

async def login_user(client, username='testuser', password='testpass'):
    data = {'username': username, 'password': password}
    r = await client.post('/api/v1/auth/login', data=data)
    print('Login status:', r.status_code, r.text)
    return r.json()['access_token']

async def get_me(client, token):
    headers = {'Authorization': f'Bearer {token}'}
    r = await client.get('/api/v1/auth/me', headers=headers)
    print('Me endpoint:', r.status_code, r.text)

async def main():
    async with httpx.AsyncClient(base_url='http://127.0.0.1:8000') as client:
        await health_check(client)
        token = await register_user(client)
        token = await login_user(client)
        await get_me(client, token)

if __name__ == '__main__':
    asyncio.run(main())
