import urllib.request
import json
import urllib.error
import urllib.parse

def get_token():
    data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8000/api/v1/auth/login', data=data)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())['access_token']

token = get_token()

# Testing out of range date
data = {
  "course_code": "AIT210",
  "exam_type": "Vize",
  "date": "2026-11-10",
  "start_time": "09:00",
  "duration_minutes": 90,
  "rooms": [
    {
      "room_code": "A101",
      "invigilator_id": 1
    }
  ]
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/scheduling/confirm", 
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
)

try:
    with urllib.request.urlopen(req) as response:
        print("Success:", response.getcode())
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print("Error:", e.code)
    print(e.read().decode())
