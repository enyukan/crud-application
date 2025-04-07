from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Replace with your actual database credentials
DATABASE_URL = "postgresql://postgres:qcadmin@localhost:5432/qc_lab_db"

# Database engine
engine = create_engine(DATABASE_URL, echo=True)

# Session maker to interact with the DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
