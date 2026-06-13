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

# 轻量迁移：create_all 不会给已存在的表加新列，这里手动补
_MIGRATIONS = [
    ("books", "tags", "JSON"),
    ("books", "word_count", "INTEGER"),
    ("writing_cards", "tags", "JSON"),
]


def _migrate():
    from sqlalchemy import text

    with engine.connect() as conn:
        for table, column, coltype in _MIGRATIONS:
            try:
                cols = [
                    row[1]
                    for row in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
                ]
                if cols and column not in cols:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}"))
                    conn.commit()
                    print(f"[DB] migrated: {table}.{column}")
            except Exception as e:
                print(f"[DB] migration {table}.{column} failed: {e}")


def init_db():
    print("[DB] init_db() called - creating tables...")
    Base.metadata.create_all(bind=engine)
    _migrate()
    print("[DB] init_db() done - tables created")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
