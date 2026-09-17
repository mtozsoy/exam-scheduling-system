import urllib.request
import json
import urllib.parse
import pytest

def get_token():
    data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8000/api/v1/auth/login', data=data)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())['access_token']

def test_courses_crud():
    token = get_token()
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Create
    course_data = {"course_code": "TESTCOURSE101", "course_name": "Test Course", "term": 1, "semester": 1}
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/courses", data=json.dumps(course_data).encode(), headers=headers, method='POST')
    with urllib.request.urlopen(req) as response:
        assert response.getcode() == 200
        
    # Update
    update_data = {"course_name": "Updated Test Course"}
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/courses/TESTCOURSE101", data=json.dumps(update_data).encode(), headers=headers, method='PUT')
    with urllib.request.urlopen(req) as response:
        assert response.getcode() == 200
        
    # Delete
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/courses/TESTCOURSE101", headers=headers, method='DELETE')
    with urllib.request.urlopen(req) as response:
        assert response.getcode() == 200
