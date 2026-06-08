from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    outline = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    author_id = Column(String)
    source = Column(String, default="local")
    peer_origin = Column(String, nullable=True)

class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(String, ForeignKey("books.id"))
    index = Column(Integer)
    title = Column(String)
    content = Column(Text)
