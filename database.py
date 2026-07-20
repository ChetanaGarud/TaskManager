from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Database file destination
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 2. Create the engine (SQLite requires check_same_thread=False)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create Base class for our upcoming models
Base = declarative_base()

# 5. DB Dependency to yield connection per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()