from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.students import router as students_router
from app.api.routes.courses import router as courses_router
from app.api.routes.teachers import router as teachers_router
from app.api.routes.invigilators import router as invigilators_router
from app.api.routes.exams import router as exams_router
from app.api.routes.rooms import router as rooms_router
from app.api.routes.scheduling import router as scheduling_router
from app.api.routes.academic_calendars import router as academic_calendars_router
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router

import os

app = FastAPI()

frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router_prefix = "/api/v1"

app.include_router(students_router, prefix=router_prefix)
app.include_router(courses_router, prefix=router_prefix)
app.include_router(teachers_router, prefix=router_prefix)
app.include_router(invigilators_router, prefix=router_prefix)
app.include_router(exams_router, prefix=router_prefix)
app.include_router(rooms_router, prefix=router_prefix)
app.include_router(academic_calendars_router, prefix=router_prefix)
app.include_router(scheduling_router, prefix=router_prefix)
app.include_router(auth_router, prefix=router_prefix)
app.include_router(users_router, prefix=router_prefix)