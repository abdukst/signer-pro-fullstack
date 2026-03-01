from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.routers.user_router import router as user_router
from app.routers.auth_router import router as auth_router
from app.routers.file_router import router as file_router
from app.database import Base, engine

from fastapi.middleware.cors import CORSMiddleware


# Look at all models that inherit from Base and create tables if they don’t exist.
Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
  # this turns a python ValueError into a clean 400 Bad Request
  return JSONResponse(
    status_code=400,
    content={"detail": str(exc)} # This sends your specific message (e.g. "Email already in use")
  )
# 1. Catch your custom Validation Errors (ValueError)
@app.exception_handler(RequestValidationError)
async def validation_excepton_handler(request: Request, exc: RequestValidationError):
  # This takes Pydantic's messy error and grabs just the first message
  # For example: "password -> String should have at least 8 characters"
  
  # 1. Get the list of errors
  errors = exc.errors()
  # 2. Grab the FIRST error in that list
  first_error = errors[0]
  # 3. Extract the field name and the message safely
  # 'loc' is a tuple like ('body', 'email'), so [-1] is 'email'
  field = first_error["loc"][-1]
  err_msg = first_error["msg"]
  return JSONResponse(
    status_code=422, # Standard code for validation errors
    content={"detail": f"{field}:{err_msg}"}
  )
# 2. Catch Database Errors (SQLAlchemyError)
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request:Request, exc:SQLAlchemyError):
  return JSONResponse(
    status_code=500,
    content={"detail":"A database error occurred. Please try again later."}                  )

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(file_router)
@app.get("/")
def health_check():
  return {"ststus": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)