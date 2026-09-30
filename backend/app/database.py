import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db(max_retries: int = 15, delay: int = 2):
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database is ready!")
            return
        except Exception as e:
            print(f"⏳ Waiting for database... ({attempt + 1}/{max_retries}): {e}")
            time.sleep(delay)
    raise RuntimeError("Could not connect to the database after several retries.")

