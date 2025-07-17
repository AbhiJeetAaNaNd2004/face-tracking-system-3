from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import time

from app.routers import streaming, embeddings, employees, attendance, auth
from app.config import settings
from utils.logging import setup_logging, get_logger, log_request
from tasks.camera_tasks import start_background_monitoring, stop_background_monitoring
from db.db_config import create_tables
from db.db_manager import DatabaseManager

# Setup logging
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    logger.info("🚀 Starting Face Tracking System API")
    
    try:
        # Initialize database tables
        create_tables()
        logger.info("✅ Database tables initialized")
        
        # Initialize master admin account
        db_manager = DatabaseManager()
        master_email, master_password = db_manager.create_master_admin()
        
        if master_email and master_password:
            logger.info("=" * 60)
            logger.info("🔐 MASTER ADMIN ACCOUNT CREATED")
            logger.info("=" * 60)
            logger.info(f"Email: {master_email}")
            logger.info(f"Password: {master_password}")
            logger.info("=" * 60)
            logger.info("⚠️  SAVE THESE CREDENTIALS SECURELY - THEY WILL NOT BE SHOWN AGAIN!")
            logger.info("=" * 60)
            
            # Also print to console for visibility
            print("\n" + "=" * 60)
            print("🔐 MASTER ADMIN ACCOUNT CREATED")
            print("=" * 60)
            print(f"Email: {master_email}")
            print(f"Password: {master_password}")
            print("=" * 60)
            print("⚠️  SAVE THESE CREDENTIALS SECURELY - THEY WILL NOT BE SHOWN AGAIN!")
            print("=" * 60 + "\n")
        else:
            logger.info("✅ Master admin account already exists")
        
        # Start background camera monitoring if enabled
        if settings.ENVIRONMENT != "testing":
            start_background_monitoring()
            logger.info("✅ Background camera monitoring started")
        
        logger.info("🎯 Face Tracking System API is ready!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown procedures
    logger.info("🛑 Shutting down Face Tracking System API")
    try:
        stop_background_monitoring()
        logger.info("✅ Background monitoring stopped")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

app = FastAPI(
    title="Face Tracking System API",
    description="Professional backend for face detection, recognition, and attendance tracking with role-based user management",
    version="2.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    log_request(
        logger=logger,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=process_time
    )
    
    return response

# Security middleware
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure this properly for production
    )

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(streaming.router)
app.include_router(embeddings.router)
app.include_router(employees.router)
app.include_router(attendance.router)

@app.get("/")
async def root():
    return {
        "message": "Face Tracking System API Running",
        "version": "2.0.0",
        "features": [
            "Role-based User Management",
            "Face Recognition & Attendance Tracking",
            "Real-time Camera Streaming",
            "Employee Management",
            "Master Admin System"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT
    }