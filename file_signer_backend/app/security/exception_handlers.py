import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

# this logger will be labeled "app.security.exception_handlers" in logs
#  logs tell us exactly which file caught the error.
logger = logging.getLogger(__name__)

def register_exception_handlers(app):
  
  # 1.catch validation Errors (e.g, bad email format)
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
    detail = f"{field}:{err_msg}"

    # We log this as a WARNING because it's a user mistake, not a server crash
    logger.warning(f"Validation failed for {request.url.path}: {detail}")

    return JSONResponse(
      status_code = status.HTTP_422_UNPROCESSABLE_CONTENT, # Standard code for validation errors
      content={"detail": detail}
    )
  
  # 2. Catch Custom Value Errors (e.g., "Invalid Password", "Email in use")
  @app.exception_handler(ValueError)
  async def value_error_handler(request: Request, exc: ValueError): 
    # this turns a python ValueError into a clean 400 Bad Request
    detail = str(exc)
    # Log the specific business logic error
    logger.warning(f"Value Error at {request.url.path}: {detail}")
    return JSONResponse(
      status_code=status.HTTP_400_BAD_REQUEST,
      content={"detail": detail} # This sends your specific message (e.g. "Email already in use")
    )
  
  # 3. Catch Database Errors (The "Critical" one)
  @app.exception_handler(SQLAlchemyError)
  async def sqlalchemy_exception_handler(request:Request, exc:SQLAlchemyError):

    # exc_info=True saves the FULL technical traceback to app.log
    # This is what to use to fix bugs later!
    logger.error(f"Database error during {request.method} {request.url.path}", exc_info=True)

    return JSONResponse(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      content={"detail":"A database error occurred. Please try again later."})
  
  # 4. Global Catch-All (For unexpected crashes)
  @app.exception_handler(Exception)
  async def general_exception_handler(request: Request, exc: Exception):

    logger.error(f"UNEXPECTED CRASH at {request.url.path}: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected technical error occurred."}
    )