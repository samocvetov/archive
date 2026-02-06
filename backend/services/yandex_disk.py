"""
Yandex Disk API Integration Service
"""
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

YANDEX_OAUTH_URL = "https://oauth.yandex.ru"
YANDEX_DISK_API_URL = "https://cloud-api.yandex.net/v1/disk"

class YandexDiskService:
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.headers = {"Authorization": f"OAuth {token}"} if token else {}
    
    async def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Получить информацию о пользователе"""
        if not self.token:
            return None
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{YANDEX_DISK_API_URL}/resources", 
                headers=self.headers,
                params={"path": "/"}
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
    
    async def upload_file(self, file_path: str, local_file_path: str) -> Optional[str]:
        """Загрузить файл на Яндекс.Диск"""
        if not self.token:
            return None
        
        # Получаем URL для загрузки
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{YANDEX_DISK_API_URL}/resources/upload",
                headers=self.headers,
                params={"path": file_path, "overwrite": "true"}
            ) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                upload_url = data.get("href")
        
        if not upload_url:
            return None
        
        # Загружаем файл
        async with aiohttp.ClientSession() as session:
            with open(local_file_path, 'rb') as f:
                async with session.put(upload_url, data=f) as response:
                    if response.status in [200, 201, 202]:
                        return file_path
                    return None
    
    async def get_download_link(self, file_path: str) -> Optional[str]:
        """Получить ссылку для скачивания файла"""
        if not self.token:
            return None
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{YANDEX_DISK_API_URL}/resources/download",
                headers=self.headers,
                params={"path": file_path}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("href")
                return None
    
    async def delete_file(self, file_path: str) -> bool:
        """Удалить файл с Яндекс.Диска"""
        if not self.token:
            return False
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{YANDEX_DISK_API_URL}/resources",
                headers=self.headers,
                params={"path": file_path, "permanently": "true"}
            ) as response:
                return response.status in [200, 202, 204]
    
    async def create_folder(self, folder_path: str) -> bool:
        """Создать папку на Яндекс.Диске"""
        if not self.token:
            return False
        
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{YANDEX_DISK_API_URL}/resources",
                headers=self.headers,
                params={"path": folder_path}
            ) as response:
                return response.status in [200, 201]
    
    async def publish_file(self, file_path: str) -> Optional[str]:
        """Опубликовать файл и получить публичную ссылку"""
        if not self.token:
            return None
        
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{YANDEX_DISK_API_URL}/resources/publish",
                headers=self.headers,
                params={"path": file_path}
            ) as response:
                if response.status == 200:
                    # Получаем публичную ссылку
                    async with session.get(
                        f"{YANDEX_DISK_API_URL}/resources",
                        headers=self.headers,
                        params={"path": file_path}
                    ) as info_response:
                        if info_response.status == 200:
                            data = await info_response.json()
                            return data.get("public_url")
                return None

# Генерация URL для авторизации OAuth
def get_yandex_oauth_url(client_id: str, redirect_uri: str) -> str:
    """Получить URL для авторизации в Яндекс"""
    return (
        f"{YANDEX_OAUTH_URL}/authorize?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}"
    )

async def exchange_code_for_token(
    client_id: str, 
    client_secret: str, 
    code: str
) -> Optional[Dict[str, Any]]:
    """Обменять код авторизации на токен"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{YANDEX_OAUTH_URL}/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret
            }
        ) as response:
            if response.status == 200:
                return await response.json()
            return None
