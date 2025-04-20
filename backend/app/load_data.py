import os
import csv
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext

from app.config.database import AsyncSessionLocal, create_tables
from app.models.models import Product, User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Utilities ---

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def insert_products(session: AsyncSession, csv_path: str) -> None:
    """Insert initial products from CSV if not already present."""
    result = await session.execute(select(Product.id))
    if result.scalar() is None:
        try:
            df = pd.read_csv(csv_path)
            products = [
                Product(
                    id=row["id"],
                    name=row["name"],
                    category=row["category"],
                    price=row["price"]
                )
                for _, row in df.iterrows()
            ]
            session.add_all(products)
        except Exception as e:
            raise RuntimeError(f"Failed to insert products: {e}")

async def insert_users(session: AsyncSession, csv_path: str) -> None:
    """Insert initial users from CSV if not already present."""
    result = await session.execute(select(User.id))
    if result.scalar() is None:
        try:
            with open(csv_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                users = []
                for row in reader:
                    if not all(k in row for k in ("id", "username", "email", "hashed_password", "role")):
                        raise ValueError(f"Incomplete user row: {row}")
                    user = User(
                        id=int(row["id"]),
                        username=row["username"].strip().lower(),
                        email=row["email"].strip().lower(),
                        hashed_password=hash_password(row["hashed_password"]),
                        role=row["role"].strip().lower()
                    )
                    users.append(user)
                session.add_all(users)
        except Exception as e:
            raise RuntimeError(f"Failed to insert users: {e}")

# --- Main initializer ---

async def insert_initial_data():
    async with AsyncSessionLocal() as session:
        try:
            await create_tables()
            await insert_products(session, "data/delta/data.csv")
            await insert_users(session, "data/delta/users.csv")
            await session.commit()
            print("Initial data inserted successfully.")
        except Exception as e:
            await session.rollback()
            print(f"Error inserting initial data: {e}")

# --- Entry point ---

if __name__ == "__main__":
    import asyncio
    asyncio.run(insert_initial_data())
