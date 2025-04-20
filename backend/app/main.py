import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from app.routes import products, users

# --- Load environment configuration ---
load_dotenv()

APP_TITLE = os.getenv("APP_TITLE", "fastAPIStartKit")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "fastAPIStartKit")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
RATE_LIMIT_GLOBAL = os.getenv("RATE_LIMIT_GLOBAL", "100/minute")
ALLOWED_ORIGINS = os.getenv("URL", "").split(",")

# --- Application instance ---
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

# --- Middleware: CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Add methods only as needed
    allow_headers=["Authorization", "Content-Type"],  # Restrict to necessary headers
)

# --- Middleware: Rate Limiting ---
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[RATE_LIMIT_GLOBAL],
)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# --- Routers ---
app.include_router(products.router)
app.include_router(users.router)
