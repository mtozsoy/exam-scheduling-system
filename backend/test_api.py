import urllib.request
import json
import urllib.error

data = {
  "course_code": "string",
  "exam_type": "string",
  "date": "2026-08-11",
  "start_time": "15:28:00",
  "duration_minutes": 0,
  "rooms": [
    {
      "room_code": "string",
      "invigilator_id": 0
    }
  ]
}

req = urllib.request.Request(
    "http://localhost:8000/scheduling/confirm", 
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        print("Success:", response.getcode())
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print("Error:", e.code)
    print(e.read().decode())
