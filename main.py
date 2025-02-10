"""
This module initializes and configures a FastAPI application.

It includes various API routers, middleware configurations,
and an exception handler for rate limiting.
"""

import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
from src.services.auth import get_current_admin_user
from src.database.models import User


from src.api import auth, contacts, users, utils, reset_password
from src.conf import messages

# Initialize FastAPI application
app = FastAPI()

# Include API routers
app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
# app.include_router(reset_password.router, prefix="/api")

# Configure CORS (Cross-Origin Resource Sharing)
origins = ["http://localhost:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handles rate limit exceeded exceptions.

    Args:
        request (Request): The incoming request that exceeded the rate limit.
        exc (RateLimitExceeded): The exception containing rate limit details.

    Returns:
        JSONResponse: A response with status code 429 and an error message.
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": f"Rate limit exceeded ({exc.detail}). Please try again later."
        },
    )

@app.get("/")
async def root():
    """
    Root endpoint of the API.

    Returns:
        dict: A welcome message.
    """
    return {"message": messages.WELCOME_MESSAGE}

@app.get("/admin")
def read_admin(current_user: User = Depends(get_current_admin_user)):
    return {"message": f"Вітаємо, {current_user.username}! Це адміністративний маршрут"}


if __name__ == "__main__":
    """
    Runs the FastAPI application using Uvicorn.
    """
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, workers=1)


