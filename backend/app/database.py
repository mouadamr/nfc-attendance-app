import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load variables from .env into the environment
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found. Check your .env file.")

# The engine manages the actual connection to Postgres
engine = create_engine(DATABASE_URL)

# Each request will get its own database session from this
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All our table models will inherit from this Base class
Base = declarative_base()

# Dependency function — FastAPI will call this for every request that needs DB access
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()