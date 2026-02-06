from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Table, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from config import settings

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Yandex Disk integration
    yandex_disk_token = Column(String, nullable=True)
    yandex_disk_refresh_token = Column(String, nullable=True)
    yandex_disk_token_expires = Column(DateTime, nullable=True)
    yandex_disk_folder = Column(String, default="/archive_videos")
    
    videos = relationship("Video", back_populates="owner")

class CaptchaSession(Base):
    __tablename__ = 'captcha_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used = Column(Boolean, default=False)

video_tags = Table(
    'video_tags',
    Base.metadata,
    Column('video_id', Integer, ForeignKey('videos.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

fragment_tags = Table(
    'fragment_tags',
    Base.metadata,
    Column('fragment_id', Integer, ForeignKey('fragments.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    filename = Column(String, unique=True, index=True)
    original_filename = Column(String)
    title = Column(String)
    duration = Column(Float)
    filepath = Column(String)
    file_size = Column(Integer)
    mime_type = Column(String)
    
    category = Column(String)
    subcategory = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="videos")
    fragments = relationship("Fragment", back_populates="video", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=video_tags, back_populates="videos")

class Fragment(Base):
    __tablename__ = 'fragments'
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey('videos.id'))
    name = Column(String)
    description = Column(Text)
    
    start_time = Column(Float)
    end_time = Column(Float)
    
    filepath = Column(String)  # Путь к превью/скриншоту
    file_size = Column(Integer)
    video_filepath = Column(String)  # Путь к видеофайлу фрагмента
    video_file_size = Column(Integer)  # Размер видеофайла
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    video = relationship("Video", back_populates="fragments")
    tags = relationship("Tag", secondary=fragment_tags, back_populates="fragments")

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    videos = relationship("Video", secondary=video_tags, back_populates="tags")
    fragments = relationship("Fragment", secondary=fragment_tags, back_populates="tags")
