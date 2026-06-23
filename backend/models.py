from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, Boolean, LargeBinary
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
    tags = Column(JSON, nullable=True)  # 标签：用户自填或 AI 生成
    word_count = Column(Integer, nullable=True)  # 全书字数（书架视图厚度依据）


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


class ProviderConfig(Base):
    __tablename__ = "provider_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    api_key = Column(Text, nullable=True)
    base_url = Column(String, nullable=True)
    models = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ActiveModel(Base):
    __tablename__ = "active_model"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class AppSetting(Base):
    """通用键值设置表（如 web 搜索 provider / api key）。"""

    __tablename__ = "app_settings"

    key = Column(String, primary_key=True)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class KnowledgeSource(Base):
    """RAG 知识源：投递的本地文档 / 内置库条目 / 纯文本。

    category: writing_guide(写作指导) | style(风格库) | reference(资料库) | continuation(续写)
    link_mode: copy(复制进数据目录) | link(引用原路径，类似软链接) | builtin(内置只读)
    """

    __tablename__ = "knowledge_sources"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    link_mode = Column(String, default="copy")
    file_path = Column(String, nullable=True)  # link/builtin 模式指向原文件；copy 模式指向数据目录副本
    text_content = Column(Text, nullable=True)  # 纯文本投递时直接存内容
    prompt = Column(Text, nullable=True)  # 配套 prompt（“文档内容 + prompt”）
    language = Column(String, nullable=True)
    builtin = Column(Boolean, default=False)
    index_status = Column(String, default="pending")  # pending | indexing | ready | failed | bm25
    index_error = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String, index=True, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(LargeBinary, nullable=True)  # numpy float32 bytes；BM25 模式为 NULL
    embedding_model = Column(String, nullable=True)


class WritingCard(Base):
    """写作卡：五个部分 = 写作指导 + 风格库 + 资料库 + 续写 + 额外需求。"""

    __tablename__ = "writing_cards"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    writing_guide_ids = Column(JSON, default=list)
    style_ids = Column(JSON, default=list)
    reference_ids = Column(JSON, default=list)
    continuation_ids = Column(JSON, default=list)
    extra_requirements = Column(Text, nullable=True)
    tags = Column(JSON, default=list)  # 写作卡分类标签
    builtin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
