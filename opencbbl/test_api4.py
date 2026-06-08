import requests

# Test API without page
try:
    response = requests.get('http://127.0.0.1:8000/api/organizations/')
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Count: {data.get("count", 0)}')
        print(f'Results: {len(data.get("results", []))}')
    else:
        print('Error:', response.text)
except Exception as e:
    print(f'Error: {e}')
