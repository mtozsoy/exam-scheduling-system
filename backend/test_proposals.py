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

data = {
  "course_code": "AIT210",
  "exam_type": "Vize",
  "duration_minutes": 90,
  "daily_start_time": "09:00:00",
  "daily_end_time": "17:00:00"
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/scheduling/proposals", 
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
)

with urllib.request.urlopen(req) as response:
    print("Success:", response.getcode())
    res_data = json.loads(response.read().decode())
    for prop in res_data['proposals']:
        print(f"Proposal Date: {prop['date']} ({prop['start_time']} - {prop['end_time']})")
