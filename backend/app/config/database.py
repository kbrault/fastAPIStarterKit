import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app.models.models import Base

# Load environment variables
load_dotenv()

# Determine environment (Docker vs local)
is_docker = os.getenv("DOCKER_ENV", "false").lower() == "true"
database_url = os.getenv("DATABASE_URL_DOCKER" if is_docker else "DATABASE_URL_LOCAL")

if not database_url:
    raise RuntimeError("DATABASE_URL is missing. Define it in your environment variables.")

# --- Async Engine Configuration ---
engine = create_async_engine(
    database_url,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    future=True
)

# --- Async Session Factory ---
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# --- Dependency injection session ---
async def get_db():
    """
    Provide a database session via FastAPI dependency injection.
    Ensures session is cleaned up after use.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            raise HTTPException(status_code=500, detail={
                "status": "error",
                "message": f"Database error: {str(e)}",
                "code": 500
            })
        finally:
            await session.close()

# --- Initialization helper ---
async def create_tables():
    """
    Create all database tables from SQLAlchemy models.
    Called at application startup.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Failed to create tables: {e}")
