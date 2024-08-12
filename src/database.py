# setup database configuration and connection to the postgresql database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# database configuration
DATABASE_URL = "postgresql+psycopg2://app_user:app_password@db/app"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
