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

class GenerationHistory(Base):
    __tablename__ = "generation_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(String, nullable=True)  # 完成后关联的书籍 ID
    prompt = Column(Text, nullable=False)  # 用户输入的需求
    requirements = Column(JSON)  # 生成要求
    outline = Column(JSON)  # 大纲 (生成完成后填充)
    status = Column(String, default="pending")  # pending/completed/failed/deleted
    error_message = Column(Text, nullable=True)  # 错误信息
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)  # 完成时间
    author_id = Column(String)
