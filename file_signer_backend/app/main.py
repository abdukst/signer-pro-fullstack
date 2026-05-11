import time 
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.security.logging_config import setup_logging
from app.security.exception_handlers import register_exception_handlers
from app.routers import user_router, auth_router, file_router
from app.database import Base, engine


# 1. START THE RECORDER FIRST
setup_logging()
logger = logging.getLogger(__name__)



# Initialize DB Tables
# Look at all models that inherit from Base and create tables if they don’t exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SignerPro API")

# 2. ATTACH THE ERROR HANDLERS
register_exception_handlers(app)


# 3. THE AUTOMATIC RECORDER (Middleware)
# This intercepts EVERY request and logs the result automatically
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Calculate how long it took
    process_time = (time.time() - start_time) * 1000
    
    # Log: Method | Path | Status Code | Time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Completed in {process_time:.2f}ms"
    )
    
    return response

# 4. CORS & ROUTERS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(file_router)
@app.get("/")
def health_check():
  return {"ststus": "ok"}