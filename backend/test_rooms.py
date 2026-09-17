import urllib.request
import json
import urllib.parse
import pytest

def get_token():
    data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8000/api/v1/auth/login', data=data)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())['access_token']

def test_rooms_crud():
    token = get_token()
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Create Room
    room_data = {"room_code": "TESTROOM1", "building": "T", "floor": 1, "capacity": 30}
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/rooms", data=json.dumps(room_data).encode(), headers=headers, method='POST')
    with urllib.request.urlopen(req) as response:
        assert response.getcode() == 200
        
    # Read Rooms
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/rooms", headers=headers)
    with urllib.request.urlopen(req) as response:
        rooms = json.loads(response.read().decode())
        assert any(r['room_code'] == 'TESTROOM1' for r in rooms)
        
    # Update Room
    update_data = {"capacity": 40}
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/rooms/TESTROOM1", data=json.dumps(update_data).encode(), headers=headers, method='PUT')
    with urllib.request.urlopen(req) as response:
        assert response.getcode() == 200
        
    # Delete Room
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/rooms/TESTROOM1", headers=headers, method='DELETE')
    with urllib.request.urlopen(req) as response:
        assert response.getcode() == 200
