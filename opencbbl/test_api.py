import requests

# Test API
response = requests.get('http://127.0.0.1:8000/api/locations/?address__icontains=Алтайский край&is_geocoded=true')
print(f'Status: {response.status_code}')
data = response.json()
print(f'Count: {data.get("count", 0)}')
print(f'Results: {len(data.get("results", []))}')

if data.get('results'):
    print('First result:', data['results'][0])
