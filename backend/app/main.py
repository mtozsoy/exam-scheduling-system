from fastapi import FastAPI

from app.api.routes.students import router as students_router
from app.api.routes.courses import router as courses_router
from app.api.routes.teachers import router as teachers_router

app = FastAPI()
app.include_router(students_router)
app.include_router(courses_router)
app.include_router(teachers_router)