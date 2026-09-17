import pytest
import threading
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import select
import os

from app.main import app
from app.db.database import get_db, Base
from app.models.room import Room
from app.models.invigilator import Invigilator
from app.models.course import Course
from app.models.academic_calendar import AcademicCalendar
from app.models.exam import Exam

# Use the real database to test real locking behavior
# The test will create a course, room, invigilator, then attempt 2 concurrent confirmations
# Then it will clean up

@pytest.fixture(scope="module")
def client_real_db():
    # We will use the main db, so we need to be careful with cleanup
    from app.db.database import engine, SessionLocal
    # ensure it's not a sqlite memory db
    
    db = SessionLocal()
    # Cleanup previous leftovers
    exams_to_delete = db.execute(select(Exam.exam_id).where(Exam.course_code == 'RACE101')).scalars().all()
    if exams_to_delete:
        from app.models.student_exam_room import StudentExamRoom
        from app.models.exam_room import ExamRoom
        from app.models.exam_invigilator import ExamInvigilator
        db.execute(StudentExamRoom.__table__.delete().where(StudentExamRoom.exam_id.in_(exams_to_delete)))
        db.execute(ExamRoom.__table__.delete().where(ExamRoom.exam_id.in_(exams_to_delete)))
        db.execute(ExamInvigilator.__table__.delete().where(ExamInvigilator.exam_id.in_(exams_to_delete)))
    db.execute(Exam.__table__.delete().where(Exam.course_code == 'RACE101'))
    db.execute(Course.__table__.delete().where(Course.course_code == 'RACE101'))
    db.execute(Room.__table__.delete().where(Room.room_code == 'RACEROOM'))
    db.execute(Invigilator.__table__.delete().where(Invigilator.first_name == 'Race'))
    db.execute(AcademicCalendar.__table__.delete().where(AcademicCalendar.exam_type == 'RaceExam'))
    db.commit()

    # Create test data
    c = Course(course_code='RACE101', course_name='Race Test', semester=1, term=1)
    r = Room(room_code='RACEROOM', building='R', floor=1, capacity=50)
    i = Invigilator(first_name='Race', last_name='Test')
    ac = AcademicCalendar(
        academic_year='2026-2027', 
        semester='Güz', 
        exam_type='RaceExam', 
        start_date='2026-11-01', 
        end_date='2026-11-30', 
        is_active=True
    )
    db.add_all([c, r, i, ac])
    db.commit()
    db.refresh(i)
    
    yield TestClient(app), i.invigilator_id
    
    # Cleanup
    exams_to_delete = db.execute(select(Exam.exam_id).where(Exam.course_code == 'RACE101')).scalars().all()
    if exams_to_delete:
        from app.models.student_exam_room import StudentExamRoom
        from app.models.exam_room import ExamRoom
        from app.models.exam_invigilator import ExamInvigilator
        db.execute(StudentExamRoom.__table__.delete().where(StudentExamRoom.exam_id.in_(exams_to_delete)))
        db.execute(ExamRoom.__table__.delete().where(ExamRoom.exam_id.in_(exams_to_delete)))
        db.execute(ExamInvigilator.__table__.delete().where(ExamInvigilator.exam_id.in_(exams_to_delete)))
    db.execute(Exam.__table__.delete().where(Exam.course_code == 'RACE101'))
    db.execute(Course.__table__.delete().where(Course.course_code == 'RACE101'))
    db.execute(Room.__table__.delete().where(Room.room_code == 'RACEROOM'))
    db.execute(Invigilator.__table__.delete().where(Invigilator.first_name == 'Race'))
    db.execute(AcademicCalendar.__table__.delete().where(AcademicCalendar.exam_type == 'RaceExam'))
    db.commit()
    db.close()

def test_concurrent_scheduling_race_condition(client_real_db):
    client, invig_id = client_real_db
    
    # We will fire two threads hitting /api/v1/scheduling/confirm at the exact same time
    # They will both try to book RACEROOM and invig_id at 2026-11-05 10:00 for RACE101
    
    payload = {
        "course_code": "RACE101",
        "exam_type": "RaceExam",
        "date": "2026-11-05",
        "start_time": "10:00:00",
        "duration_minutes": 90,
        "rooms": [
            {
                "room_code": "RACEROOM",
                "invigilator_id": invig_id
            }
        ]
    }
    
    results = []
    
    login_resp = client.post("/api/v1/auth/login", data={"username": "admin", "password": "admin123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    def worker():
        resp = client.post("/api/v1/scheduling/confirm", json=payload, headers=headers)
        results.append(resp)
        
    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    # One should succeed (200), one should fail (409 Conflict)
    status_codes = [r.status_code for r in results]
    
    print("Concurrent status codes:", status_codes)
    for r in results:
        print(r.json())
        
    assert 200 in status_codes
    assert 409 in status_codes
    
