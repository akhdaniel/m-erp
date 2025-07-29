#!/usr/bin/env python3
"""
Database seeding script.
Run this script to populate the database with initial data.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import async_session_factory
from app.core.seed_data import seed_database


async def main():
  """Main function to seed the database."""
  print("Starting database seeding...")
  
  async with async_session_factory() as session:
    try:
      await seed_database(session)
      print("Database seeding completed successfully!")
    except Exception as e:
      print(f"Error during database seeding: {e}")
      raise


if __name__ == "__main__":
  asyncio.run(main())