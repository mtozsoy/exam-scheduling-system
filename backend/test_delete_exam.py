import urllib.request
import json
import urllib.error
import time

def test_delete():
    # 1. First get exams
    req_get = urllib.request.Request("http://localhost:8000/exams")
    try:
        with urllib.request.urlopen(req_get) as response:
            exams = json.loads(response.read().decode())
    except Exception as e:
        print("Failed to get exams:", e)
        return

    if not exams:
        print("No exams to delete, skipping test.")
        return
        
    # Get the last exam to delete
    exam_to_delete = exams[-1]
    exam_id = exam_to_delete["exam_id"]
    course_code = exam_to_delete["course_code"]
    
    print(f"Attempting to delete exam_id {exam_id} for course {course_code}")
    
    # 2. Delete it
    req_del = urllib.request.Request(
        f"http://localhost:8000/exams/{exam_id}", 
        method='DELETE'
    )
    
    try:
        with urllib.request.urlopen(req_del) as response:
            print("Delete Success:", response.getcode())
            print(response.read().decode())
    except urllib.error.HTTPError as e:
        print("Delete Error:", e.code)
        print(e.read().decode())
        
    # 3. Verify it is deleted (should get 404 on put or verify from get)
    req_get2 = urllib.request.Request("http://localhost:8000/exams")
    try:
        with urllib.request.urlopen(req_get2) as response:
            exams_after = json.loads(response.read().decode())
            if any(e["exam_id"] == exam_id for e in exams_after):
                print(f"[ERROR] Exam {exam_id} still exists in the list!")
            else:
                print(f"[SUCCESS] Exam {exam_id} successfully removed from the database.")
    except Exception as e:
        print("Failed to get exams after delete:", e)

if __name__ == "__main__":
    test_delete()
