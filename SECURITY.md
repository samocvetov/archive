# Security Policy

## Чувствительные данные

Проект НЕ содержит реальных чувствительных данных:
- ✅ Нет реальных API ключей
- ✅ Нет реальных паролей в коде
- ✅ Нет токенов доступа
- ✅ Нет персональных данных

## Placeholders (заглушки)

В коде используются placeholder'ы, которые необходимо заменить перед использованием:

### Backend (`backend/config.py`)
```python
SECRET_KEY = "your-secret-key-change-in-production"
```

### Backend (`backend/routers/yandex.py`)
```python
YANDEX_CLIENT_ID = "your_client_id"
YANDEX_CLIENT_SECRET = "your_client_secret"
```

### Backend (`backend/migrate_auth.py`)
```python
# Хеш пароля - замените на свой!
hashed_password = '$2b$12$YourHashedPasswordHere'
```

## Настройка перед продакшеном

1. **Сгенерируйте SECRET_KEY:**
```bash
openssl rand -hex 32
```

2. **Установите переменные окружения** в файле `.env`:
```env
SECRET_KEY=your-generated-secret-key
YANDEX_CLIENT_ID=your-yandex-client-id
YANDEX_CLIENT_SECRET=your-yandex-client-secret
```

3. **Создайте пароль для администратора:**
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("your-secure-password")
print(hashed)
```

## Файлы, которые НЕ должны попадать в Git

- `.env` - Переменные окружения
- `*.db` - Базы данных SQLite
- `data/` - Загруженные видео
- `node_modules/` - Зависимости Node.js
- `__pycache__/` - Кэш Python

## .gitignore

Проект уже содержит `.gitignore`, который исключает:
- Базы данных
- Загруженные файлы
- Переменные окружения
- Зависимости

## Сообщить об уязвимости

Если вы обнаружили реальные чувствительные данные в репозитории, пожалуйста, создайте Issue.
