from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine, SessionLocal
from app.api import auth, students, uploads, institutions, validation, analytics, verification
from app.seed_data import seed_database_defaults


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed default institutions & users if clean
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database_defaults(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="AICTE APAAR-Based Student Data Management & Verification Portal",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS: only http://localhost:5173; methods GET/POST/PATCH; headers Authorization, Content-Type
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# Mount API v1 Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(students.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1")
app.include_router(institutions.router, prefix="/api/v1")
app.include_router(validation.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(verification.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "system": "AICTE-APAAR-PLATFORM", "sandbox": "Simulated"}
