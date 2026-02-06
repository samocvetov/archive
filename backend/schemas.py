from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Auth & User schemas
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CaptchaResponse(BaseModel):
    session_id: str
    question: str

class LoginRequest(BaseModel):
    username: str
    password: str
    captcha_session_id: str
    captcha_answer: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class VideoBase(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None

class VideoCreate(VideoBase):
    pass

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None

class Video(VideoBase):
    id: int
    filename: str
    original_filename: str
    duration: Optional[float] = None
    filepath: Optional[str] = None
    file_size: int
    mime_type: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VideoWithTags(Video):
    tags: List[Tag] = []
    fragments: List['Fragment'] = []

class FragmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: float
    end_time: float

class FragmentCreate(FragmentBase):
    tag_ids: Optional[List[int]] = []

class FragmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    tag_ids: Optional[List[int]] = None

class Fragment(FragmentBase):
    id: int
    video_id: int
    filepath: Optional[str] = None  # Путь к превью/скриншоту
    file_size: Optional[int] = None
    video_filepath: Optional[str] = None  # Путь к видеофайлу фрагмента
    video_file_size: Optional[int] = None  # Размер видеофайла
    created_at: datetime
    
    class Config:
        from_attributes = True

class FragmentWithTags(Fragment):
    tags: List[Tag] = []
    video: Video

VideoWithTags.model_rebuild()
FragmentWithTags.model_rebuild()

class SearchQuery(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
