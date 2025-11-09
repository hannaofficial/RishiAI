import os, pathlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

ENV_PATH = pathlib.Path(__file__).with_name(".env")  # services/orchestrator/.env
load_dotenv(dotenv_path=ENV_PATH, override=True)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(f"DATABASE_URL is not set. Expected in {ENV_PATH}")

engine = create_engine(DATABASE_URL, pool_pre_ping=True , future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
