import os
import csv
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import AsyncSessionLocal
from app.models.models import Product, User
from sqlalchemy.inspection import inspect

EXPORT_FOLDER = "data/export"

def get_timestamp():
    """Generate current timestamp in YYYYMMDD_HHMMSS format."""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

async def export_table_to_csv(session: AsyncSession, model, filename):
    """Export data from a table to CSV with timestamp."""
    try:
        result = await session.execute(select(model))
        rows = result.scalars().all()

        if not rows:
            print(f"No data to export for {model.__tablename__}")
            return

        os.makedirs(EXPORT_FOLDER, exist_ok=True)

        timestamp = get_timestamp()
        file_path = os.path.join(EXPORT_FOLDER, f"{filename}_{timestamp}.csv")

        columns = [col.name for col in inspect(model).columns]

        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow({col: getattr(row, col) for col in columns})

        print(f"Exported {model.__tablename__} to {file_path}")
    except Exception as e:
        print(f"Error exporting {model.__tablename__}: {e}")

async def export_database():
    """Export all tables to CSV format."""
    async with AsyncSessionLocal() as session:
        await export_table_to_csv(session, Product, "products")
        await export_table_to_csv(session, User, "users")

if __name__ == "__main__":
    import asyncio
    asyncio.run(export_database())