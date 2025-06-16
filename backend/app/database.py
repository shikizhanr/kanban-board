import os
import warnings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    if "asyncpg" in DATABASE_URL or "aiomysql" in DATABASE_URL or "aiosqlite" in DATABASE_URL:
        warnings.warn(
            f"Warning: DATABASE_URL ('{DATABASE_URL}') appears to use an asynchronous driver "
            "with a synchronous SQLAlchemy engine. Please use a synchronous driver "
            "(e.g., psycopg2, mysqlclient) or switch to an asynchronous engine if intended."
        )
else:
    warnings.warn(
        "Warning: DATABASE_URL is not set. The application might not be able to connect to the database."
    )

# Ensure DATABASE_URL is not None before creating engine, or provide a default/handle error
if not DATABASE_URL:
    # Fallback to a default local URL or raise an error, depending on desired behavior
    # For now, let's print a critical warning and it will likely fail at create_engine
    print("CRITICAL: DATABASE_URL is not set. SQLAlchemy engine creation will likely fail.")
    # Or raise ValueError("DATABASE_URL environment variable is not set.")

engine = create_engine(DATABASE_URL if DATABASE_URL else "sqlite:///:memory:") # Added a fallback to prevent None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()