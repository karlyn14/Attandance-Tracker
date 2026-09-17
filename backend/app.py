import sys
import os

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import API_TITLE, API_VERSION, API_DESCRIPTION
from backend.routes.students import router as students_router
from backend.routes.attendance import router as attendance_router
from backend.routes.risk import router as risk_router

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION
)

# Enable CORS for frontend dashboard (Streamlit / React / Vue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(students_router)
app.include_router(attendance_router)
app.include_router(risk_router)

@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint returning API status.
    """
    return {
        "status": "healthy",
        "service": API_TITLE,
        "version": API_VERSION,
        "endpoints": [
            "/students",
            "/student/{id}",
            "/attendance/{id}",
            "/risk/{id}",
            "/docs"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Member 10 Attendance Monitoring Backend API server on http://127.0.0.1:8000 ...")
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
