from typing import List, Optional, Union, Generic, TypeVar
from pydantic import BaseModel, Field, EmailStr

# Type générique pour les réponses
T = TypeVar("T")

# --- Standardized Response ---

class StandardResponse(BaseModel, Generic[T]):
    """Generic API response schema"""
    status: str = Field(..., description="Response status: 'success' or 'error'")
    message: str = Field(..., description="Human-readable status message")
    data: Optional[T] = Field(None, description="Payload: object, list, or None")
    errors: Optional[List[dict]] = Field(default_factory=list, description="Validation or domain-specific errors")
    code: int = Field(..., description="HTTP status code")


# --- User Schemas ---

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="User password")

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str


# --- Product Schemas ---

class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Product name")
    category: str = Field(..., min_length=3, max_length=100, description="Product category")
    price: float = Field(..., gt=0, description="Product price")

class ProductCreate(ProductBase):
    """Schema used for product creation (input)"""
    pass

class ProductOut(BaseModel):
    id: int
    name: str
    category: str
    price: float
