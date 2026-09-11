from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import employees

app = FastAPI(
    title="NFC Attendance API",
    description="Backend for the NFC-based attendance tracking app",
    version="0.1.0"
)

# Allows your Android app (and testing tools) to call this API
# For now, wide open — we'll restrict this later once we know the app's real origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "NFC Attendance API is running"}