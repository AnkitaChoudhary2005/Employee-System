from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.utlis.settings import settings


# Database connection
engine = create_engine(
    settings.DB_CONNECTION,
    pool_pre_ping=True
)

# Base class for all database models
Base = declarative_base()

# Database session factory
LocalSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Dependency used by FastAPI routes
def get_db():
    db = LocalSession()

    try:
        yield db
    finally:
        db.close()
