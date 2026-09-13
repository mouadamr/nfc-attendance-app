from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import employees, cards, attendance

app = FastAPI(
    title="NFC Attendance API",
    description="Backend for the NFC-based attendance tracking app",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(cards.router)
app.include_router(attendance.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "NFC Attendance API is running"}