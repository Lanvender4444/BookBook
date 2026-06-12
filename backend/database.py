import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from utils import get_app_data_dir

DATA_DIR = get_app_data_dir() / "data"
print(f"[DB] Data dir: {DATA_DIR}")
print(f"[DB] Data dir exists: {DATA_DIR.exists()}, is_dir: {DATA_DIR.is_dir() if DATA_DIR.exists() else 'N/A'}")
try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[DB] mkdir OK, path={DATA_DIR}")
except Exception as e:
    print(f"[DB] mkdir FAILED: {e}")

DATABASE_URL = f"sqlite:///{(DATA_DIR / 'ebooks.db').as_posix()}"
print(f"[DB] DATABASE_URL={DATABASE_URL}")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
print(f"[DB] Engine created OK")
SessionLocal = sessionmaker(bind=engine)
print(f"[DB] SessionLocal created OK")

def init_db():
    print("[DB] init_db() called - creating tables...")
    Base.metadata.create_all(bind=engine)
    print("[DB] init_db() done - tables created")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
