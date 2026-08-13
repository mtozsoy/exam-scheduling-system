import urllib.request
import json
import urllib.error

data = {
  "course_code": "BMU402",
  "exam_type": "Vize",
  "duration_minutes": 90,
  "daily_start_time": "09:00:00",
  "daily_end_time": "17:00:00"
}

req = urllib.request.Request(
    "http://localhost:8000/scheduling/proposals", 
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        print("Success:", response.getcode())
        resp_data = json.loads(response.read().decode())
        if resp_data.get("success"):
            # Check the dates of the first few proposals
            for p in resp_data["proposals"][:2]:
                print(f"Proposal Date: {p['date']} ({p['start_time']} - {p['end_time']})")
        else:
            print(resp_data)
except urllib.error.HTTPError as e:
    print("Error:", e.code)
    print(e.read().decode())
