import httpx, sys
try:
    r = httpx.get('http://localhost:9200')
    print('Status', r.status_code)
    print(r.text)
except Exception as e:
    print('Error', e)