import argparse
import uvicorn
import asyncio
from app.load_data import insert_initial_data
from app.export_db import export_database

def launch_app():
    """Start FastAPI"""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)

def load_data():
    """Load initial data"""
    asyncio.run(insert_initial_data())

def export_data():
    """Export full database to CSV"""
    asyncio.run(export_database())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage API execution")
    parser.add_argument(
        "mode",
        choices=["app", "load", "export"],
        help="Choose 'app' to start FastAPI, 'load' to insert data, or 'export' to save database to CSV."
    )

    args = parser.parse_args()

    if args.mode == "app":
        launch_app()
    elif args.mode == "load":
        load_data()
    elif args.mode == "export":
        export_data()
