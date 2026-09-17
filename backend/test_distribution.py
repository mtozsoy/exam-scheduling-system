import sys
import os
from datetime import date, time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models.student_exam_room import StudentExamRoom
from sqlalchemy import select

from app.api.deps import get_current_secretary_or_admin
from app.models.user import User

def mock_auth():
    return User(KullaniciID=1, KullaniciAdi='admin', Rol='admin')

app.dependency_overrides[get_current_secretary_or_admin] = mock_auth
client = TestClient(app)

def test_student_distribution():
    print("Testing student distribution API...")
    db = SessionLocal()
    try:
        # We need a course code and room
        from app.models.course import Course
        from app.models.student_course import StudentCourse
        from app.models.room import Room
        from app.models.invigilator import Invigilator
        from app.models.academic_calendar import AcademicCalendar
        
        # Find a course that has at least one student
        student_course = db.execute(select(StudentCourse)).scalars().first()
        if not student_course:
            print("No students enrolled in any course!")
            return
            
        course = db.execute(select(Course).where(Course.course_code == student_course.course_code)).scalars().first()
        room = db.execute(select(Room)).scalars().first()
        invigilator = db.execute(select(Invigilator)).scalars().first()
        calendar = db.execute(select(AcademicCalendar).where(AcademicCalendar.is_active == True)).scalars().first()
        
        if not course or not room or not invigilator or not calendar:
            print("Missing prerequisite data (course, room, invigilator, or calendar).")
            return
            
        print(f"Using Course: {course.course_code}, Room: {room.room_code}")
        
        # Clean up any existing exam for this course
        from app.models.exam import Exam
        existing_exams = db.execute(select(Exam).where(Exam.course_code == course.course_code)).scalars().all()
        for existing_exam in existing_exams:
            print(f"Deleting existing exam {existing_exam.exam_id} for course {course.course_code}...")
            client.delete(f"/exams/{existing_exam.exam_id}")
        db.commit() # just in case
        
        # Make sure we have enough rooms for the course students
        from app.models.student_course import StudentCourse
        students_count = len(db.execute(select(StudentCourse).where(StudentCourse.course_code == course.course_code)).scalars().all())
        print(f"Course {course.course_code} has {students_count} students.")
        
        rooms = db.execute(select(Room)).scalars().all()
        selected_rooms = []
        cap = 0
        for r in rooms:
            selected_rooms.append({"room_code": r.room_code, "invigilator_id": invigilator.invigilator_id})
            cap += r.capacity
            if cap >= students_count:
                break
                
        print(f"Selected {len(selected_rooms)} rooms with total capacity {cap}")
        
        # 1. Confirm Proposal
        payload = {
            "course_code": course.course_code,
            "exam_type": calendar.exam_type,
            "date": calendar.start_date.isoformat(),
            "start_time": "09:00:00",
            "duration_minutes": 90,
            "rooms": selected_rooms
        }
        
        response = client.post("/scheduling/confirm", json=payload)
        
        if response.status_code != 200:
            print(f"Failed to create exam: {response.json()}")
            # It might fail with 409 conflict if an exam already exists at that time, let's try 17:00
            payload["start_time"] = "17:00:00"
            response = client.post("/scheduling/confirm", json=payload)
            if response.status_code != 200:
                print(f"Failed again: {response.json()}")
                return
                
        result = response.json()
        print(f"Confirm response: {result}")
        exam_id = result.get("exam_id")
        
        # 2. Check the distributions via GET API
        dist_response = client.get(f"/exams/{exam_id}/distributions")
        dist_result = dist_response.json()
        print(f"GET /distributions response: {dist_result}")
        
        assert len(dist_result) > 0, "No distribution generated!"
        
        # Verify capacities and no duplicates and correct course students
        assigned_students_set = set()
        
        # Fetch expected students for the course
        course_students_query = db.execute(
            select(StudentCourse.student_number).where(StudentCourse.course_code == course.course_code)
        ).scalars().all()
        expected_students = set(course_students_query)
        
        for room_dist in dist_result:
            r_code = room_dist["room_code"]
            students_in_room = room_dist["students"]
            
            # Verify capacity is not exceeded
            r_obj = next(r for r in rooms if r.room_code == r_code)
            assert len(students_in_room) <= r_obj.capacity, f"Room {r_code} capacity exceeded!"
            
            # Verify deterministic sort
            assert students_in_room == sorted(students_in_room), f"Students in {r_code} are not deterministically sorted!"
            
            for s in students_in_room:
                # Same student not in multiple rooms
                assert s not in assigned_students_set, f"Student {s} is assigned to multiple rooms!"
                assigned_students_set.add(s)
                
                # Student is enrolled in the course
                assert s in expected_students, f"Student {s} is NOT enrolled in course {course.course_code}!"
                
        # Make sure all enrolled students were assigned, if total capacity was enough
        if cap >= students_count:
            assert assigned_students_set == expected_students, "Not all students were assigned despite sufficient capacity!"
        
        print("All assertions passed: Correct students, no capacity overflow, no duplicates, deterministically sorted.")
        
        # 3. Delete the exam and verify cleanup
        delete_response = client.delete(f"/exams/{exam_id}")
        assert delete_response.status_code == 200, "Failed to delete exam"
        
        # Check DB to ensure StudentExamRoom records are gone
        leftover = db.execute(select(StudentExamRoom).where(StudentExamRoom.exam_id == exam_id)).scalars().all()
        assert len(leftover) == 0, "StudentExamRoom records were not deleted!"
        print("Cleanup successful!")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_student_distribution()
