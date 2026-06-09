from sqlalchemy import Column, String, Integer, Text, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    outline = Column(JSON)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    author_id = Column(String)
    source = Column(String, default="local")
    peer_origin = Column(String, nullable=True)
    language = Column(String, nullable=True)

class GenerationHistory(Base):
    __tablename__ = "generation_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(String, nullable=True)
    prompt = Column(Text, nullable=False)
    requirements = Column(JSON)
    outline = Column(JSON)
    status = Column(String, default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    author_id = Column(String)
    language = Column(String, nullable=True)

class ShareToken(Base):
    __tablename__ = "share_tokens"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, unique=True, nullable=False, index=True)
    book_id = Column(String, nullable=True)
    peer_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    used_count = Column(Integer, default=0)
