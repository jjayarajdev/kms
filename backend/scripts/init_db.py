#!/usr/bin/env python3
"""Database initialization script."""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend src directory to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.data.database import db_manager
from src.data.models import Base
from sqlalchemy.ext.asyncio import create_async_engine


async def create_tables():
    """Create all database tables."""
    try:
        print("Creating database tables...")
        
        # Create async engine
        engine = db_manager.engine
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)
    finally:
        await db_manager.close()


async def drop_tables():
    """Drop all database tables (use with caution!)."""
    try:
        print("⚠️  WARNING: Dropping all database tables...")
        response = input("Are you sure? Type 'yes' to continue: ")
        
        if response.lower() != 'yes':
            print("Operation cancelled.")
            return
        
        # Create async engine
        engine = db_manager.engine
        
        # Drop all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        print("✅ Database tables dropped successfully!")
        
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        sys.exit(1)
    finally:
        await db_manager.close()


async def reset_database():
    """Reset database (drop and recreate tables)."""
    await drop_tables()
    await create_tables()


async def check_database_connection():
    """Check if database connection is working."""
    try:
        print("Checking database connection...")
        
        async with db_manager.get_session() as session:
            result = await session.execute("SELECT 1")
            if result.scalar() == 1:
                print("✅ Database connection successful!")
            else:
                print("❌ Database connection failed!")
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python init_db.py [create|drop|reset|check]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "create":
        asyncio.run(create_tables())
    elif command == "drop":
        asyncio.run(drop_tables())
    elif command == "reset":
        asyncio.run(reset_database())
    elif command == "check":
        asyncio.run(check_database_connection())
    else:
        print("Invalid command. Use: create, drop, reset, or check")
        sys.exit(1)