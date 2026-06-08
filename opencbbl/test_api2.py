import requests

# Test API
response = requests.get('http://127.0.0.1:8000/api/locations/map_points/?address__icontains=Алтайский край')
print(f'Status: {response.status_code}')
data = response.json()
print(f'Results count: {len(data)}')

if data:
    print('First result:', data[0])
