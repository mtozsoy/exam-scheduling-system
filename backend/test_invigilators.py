import urllib.request
import json
import urllib.parse
import pytest

def get_token():
    data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8000/api/v1/auth/login', data=data)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())['access_token']

def test_invigilators_crud():
    token = get_token()
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Create
    inv_data = {"first_name": "TestFirst", "last_name": "TestLast"}
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/invigilators", data=json.dumps(inv_data).encode(), headers=headers, method='POST')
    with urllib.request.urlopen(req) as response:
        assert response.getcode() == 200
        created = json.loads(response.read().decode())
        inv_id = created["invigilator_id"]
        
    # Update
    update_data = {"first_name": "UpdatedFirst"}
    req = urllib.request.Request(f"http://127.0.0.1:8000/api/v1/invigilators/{inv_id}", data=json.dumps(update_data).encode(), headers=headers, method='PUT')
    with urllib.request.urlopen(req) as response:
        assert response.getcode() == 200
        
    # Delete
    req = urllib.request.Request(f"http://127.0.0.1:8000/api/v1/invigilators/{inv_id}", headers=headers, method='DELETE')
    with urllib.request.urlopen(req) as response:
        assert response.getcode() == 200
