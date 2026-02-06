from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import List, Optional
import random
import string
from passlib.context import CryptContext
from jose import JWTError, jwt

from database import get_db
from models import User, CaptchaSession
from schemas import UserCreate, User, CaptchaResponse, LoginRequest, Token
from config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_captcha():
    """Генерирует простую математическую капчу"""
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    question = f"{a} + {b} = ?"
    answer = str(a + b)
    return question, answer

def generate_session_id():
    """Генерирует уникальный session_id для капчи"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.get("/captcha", response_model=CaptchaResponse)
async def get_captcha(db: AsyncSession = Depends(get_db)):
    """Получить новую капчу"""
    question, answer = generate_captcha()
    session_id = generate_session_id()
    
    # Сохраняем в базу
    captcha = CaptchaSession(
        session_id=session_id,
        question=question,
        answer=answer
    )
    db.add(captcha)
    await db.commit()
    
    # Очищаем старые капчи (старше 10 минут)
    old_time = datetime.utcnow() - timedelta(minutes=10)
    await db.execute(
        select(CaptchaSession).where(CaptchaSession.created_at < old_time)
    )
    
    return CaptchaResponse(session_id=session_id, question=question)

@router.post("/register", response_model=User)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Регистрация нового пользователя"""
    # Проверяем, что пользователь не существует
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Создаем пользователя
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Вход с капчей"""
    # Проверяем капчу
    result = await db.execute(
        select(CaptchaSession).where(CaptchaSession.session_id == login_data.captcha_session_id)
    )
    captcha = result.scalar_one_or_none()
    
    if not captcha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired captcha session"
        )
    
    if captcha.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Captcha already used"
        )
    
    if captcha.answer != login_data.captcha_answer.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid captcha answer"
        )
    
    # Помечаем капчу как использованную
    captcha.used = True
    await db.commit()
    
    # Проверяем пользователя
    result = await db.execute(select(User).where(User.username == login_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    # Обновляем время входа
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Создаем токен
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}

from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> Optional[User]:
    """Получить текущего пользователя из токена (опционально)"""
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Проверить что пользователь активен (обязательно)"""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user
