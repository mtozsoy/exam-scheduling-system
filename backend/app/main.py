from fastapi import FastAPI

from app.api.routes.students import router as students_router
from app.api.routes.courses import router as courses_router
from app.api.routes.teachers import router as teachers_router
from app.api.routes.exams import router as exams_router
from app.api.routes.rooms import router as rooms_router
from app.api.routes.scheduling import router as scheduling_router

app = FastAPI()
app.include_router(students_router)
app.include_router(courses_router)
app.include_router(teachers_router)
app.include_router(exams_router)
app.include_router(rooms_router)
app.include_router(scheduling_router)