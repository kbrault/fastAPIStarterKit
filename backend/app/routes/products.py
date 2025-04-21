from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func  # Import func to count total products
from slowapi import Limiter
from slowapi.util import get_remote_address
from dotenv import load_dotenv
import os

from app.config.database import get_db
from app.config.auth import get_current_user
from app.models.models import Product
from app.utils.responses import format_response

# Load environment variables
load_dotenv()

# Configuration
DEFAULT_LIMIT = int(os.getenv("DEFAULT_LIMIT", 10))
DEFAULT_OFFSET = int(os.getenv("DEFAULT_OFFSET", 0))
RATE_LIMIT_GLOBAL = os.getenv("RATE_LIMIT_GLOBAL", "300/minute")

# Router and rate limiter
router = APIRouter(tags=["Products"])
limiter = Limiter(key_func=get_remote_address)

# --- Endpoints ---

@router.get("/api/products")
@limiter.limit(RATE_LIMIT_GLOBAL)
async def get_products(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=100, description="Number of products to return (1-100)"),
    offset: int = Query(DEFAULT_OFFSET, ge=0, description="Offset for pagination")
):
    """
    Retrieve a paginated list of products for an authenticated user, including total count for pagination.
    """

    # Get total product count for pagination
    total_count = await db.scalar(select(func.count()).select_from(Product))

    # Get paginated products
    result = await db.execute(select(Product).limit(limit).offset(offset))
    products = result.scalars().all()

    return format_response(
        status="success",
        message="Products retrieved successfully.",
        data={"products": products, "total_count": total_count},  # Include total count
        code=200
    )


@router.get("/api/product/{product_id}")
@limiter.limit(RATE_LIMIT_GLOBAL)
async def get_product(
    request: Request,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve a single product by ID for an authenticated user.
    """
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if product is None:
        return format_response(
            status="error",
            message="Product not found.",
            code=404
        )

    return format_response(
        status="success",
        message="Product retrieved successfully.",
        data=product,
        code=200
    )
