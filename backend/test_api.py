import urllib.request
import json
import urllib.error

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
