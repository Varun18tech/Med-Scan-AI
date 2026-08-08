from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from database import create_tables
from routers.auth      import router as auth_router
from routers.patients  import router as patients_router
from routers.reports   import router as reports_router
from routers.dashboard import dash_router, hist_router
from routers.analyze   import router as analyze_router

app = FastAPI(
    title       = "MedScan AI",
    description = "Intelligent Medical Report Analyzer v2.0",
    version     = "2.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)
app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(reports_router)
app.include_router(dash_router)
app.include_router(hist_router)
app.include_router(analyze_router)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
def startup():
    create_tables()
    print("MedScan AI v2.0 started successfully")
    print("API Docs: http://localhost:8000/docs")

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "version": "2.0.0"}

@app.get("/", tags=["System"])
def root():
    return {"message": "MedScan AI v2.0 - visit /docs for API reference"}