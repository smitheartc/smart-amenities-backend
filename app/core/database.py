# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# TODO: Replace with real db url and have this connect to Pooja's DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./smart_amenities.db"

# connect_args={"check_same_thread": False} is required for SQLite in FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to inject the DB session into your routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()