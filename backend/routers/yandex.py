from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from database import get_db
from models import User
from schemas import User as UserSchema
from routers.auth import get_current_active_user
from services.yandex_disk import (
    YandexDiskService, 
    get_yandex_oauth_url, 
    exchange_code_for_token
)
from config import settings

router = APIRouter(prefix="/yandex", tags=["yandex"])

# Настройки OAuth (в реальном проекте хранить в env!)
YANDEX_CLIENT_ID = settings.YANDEX_CLIENT_ID if hasattr(settings, 'YANDEX_CLIENT_ID') else "your_client_id"
YANDEX_CLIENT_SECRET = settings.YANDEX_CLIENT_SECRET if hasattr(settings, 'YANDEX_CLIENT_SECRET') else "your_client_secret"
REDIRECT_URI = settings.YANDEX_REDIRECT_URI if hasattr(settings, 'YANDEX_REDIRECT_URI') else "http://localhost:3000/yandex/callback"

@router.get("/auth-url")
async def get_auth_url(current_user: User = Depends(get_current_active_user)):
    """Получить URL для авторизации в Яндекс"""
    auth_url = get_yandex_oauth_url(YANDEX_CLIENT_ID, REDIRECT_URI)
    return {"auth_url": auth_url}

@router.post("/connect")
async def connect_yandex_disk(
    code: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Подключить Яндекс.Диск по коду авторизации"""
    token_data = await exchange_code_for_token(
        YANDEX_CLIENT_ID, 
        YANDEX_CLIENT_SECRET, 
        code
    )
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authorization code"
        )
    
    # Сохраняем токен
    current_user.yandex_disk_token = token_data.get("access_token")
    current_user.yandex_disk_refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 3600)
    from datetime import datetime, timedelta
    current_user.yandex_disk_token_expires = datetime.utcnow() + timedelta(seconds=expires_in)
    
    await db.commit()
    
    # Создаем папку на Яндекс.Диске
    yandex_service = YandexDiskService(current_user.yandex_disk_token)
    await yandex_service.create_folder(current_user.yandex_disk_folder)
    
    return {"message": "Yandex Disk connected successfully"}

@router.post("/disconnect")
async def disconnect_yandex_disk(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Отключить Яндекс.Диск"""
    current_user.yandex_disk_token = None
    current_user.yandex_disk_refresh_token = None
    current_user.yandex_disk_token_expires = None
    
    await db.commit()
    
    return {"message": "Yandex Disk disconnected"}

@router.get("/status")
async def get_disk_status(current_user: User = Depends(get_current_active_user)):
    """Проверить статус подключения Яндекс.Диска"""
    is_connected = bool(current_user.yandex_disk_token)
    disk_info = None
    
    if is_connected:
        yandex_service = YandexDiskService(current_user.yandex_disk_token)
        disk_info = await yandex_service.get_user_info()
    
    return {
        "connected": is_connected,
        "folder": current_user.yandex_disk_folder if is_connected else None,
        "disk_info": disk_info
    }

@router.get("/test")
async def test_disk_connection(current_user: User = Depends(get_current_active_user)):
    """Проверить соединение с Яндекс.Диском"""
    if not current_user.yandex_disk_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yandex Disk not connected"
        )
    
    yandex_service = YandexDiskService(current_user.yandex_disk_token)
    user_info = await yandex_service.get_user_info()
    
    if user_info:
        return {"status": "ok", "info": user_info}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
