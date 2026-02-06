# 🎬 Видео Архив

Веб-приложение для хранения, каталогизации и управления видеофайлами с возможностью создания фрагментов и интеграции с Яндекс.Диском.

## ✨ Возможности

- 📹 **Загрузка видео** - Поддержка MP4, AVI, MOV, MKV и других форматов
- ✂️ **Создание фрагментов** - Вырезание лучших моментов из видео
- 🏷️ **Теги и категории** - Удобная организация видеотеки
- 🔍 **Поиск** - Поиск по названию, категориям и тегам
- 💾 **Яндекс.Диск** - Интеграция для хранения видео в облаке
- 🔐 **Авторизация** - Защита паролем с капчей
- 📱 **Адаптивный дизайн** - Работает на всех устройствах

## 🚀 Быстрый старт (Docker)

### Требования
- Docker
- Docker Compose

### Установка

1. **Клонируй репозиторий:**
```bash
git clone https://github.com/samocvetov/archive.git
cd archive
```

2. **Запусти проект:**
```bash
docker-compose up -d
```

3. **Открой в браузере:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Остановка
```bash
docker-compose down
```

## 🔧 Ручная установка (без Docker)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python migrate.py
python migrate_auth.py
python migrate_yandex.py
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🔐 Стандартные учетные данные

- **Username:** `admin`
- **Password:** `admin123`

## 📁 Структура проекта

```
archive/
├── backend/              # FastAPI backend
│   ├── routers/         # API endpoints
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   └── services/        # Business logic
├── frontend/            # React + Vite frontend
│   ├── src/
│   │   ├── pages/      # React components
│   │   └── services/   # API client
│   └── public/
├── nginx/              # Nginx configuration
├── data/               # Uploaded videos (created automatically)
└── docker-compose.yml  # Docker orchestration
```

## 🔗 Интеграция с Яндекс.Диском

1. Создай приложение на [oauth.yandex.ru](https://oauth.yandex.ru)
2. Добавь Client ID и Secret в переменные окружения
3. Подключи Яндекс.Диск в настройках пользователя

## 🛠️ Технологии

### Backend
- **FastAPI** - Современный веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **SQLite** - База данных (легко заменить на PostgreSQL)
- **FFmpeg** - Обработка видео
- **JWT** - Аутентификация

### Frontend
- **React 18** - UI библиотека
- **TypeScript** - Типизация
- **Vite** - Сборщик
- **Tailwind CSS** - Стилизация
- **React Player** - Воспроизведение видео

### DevOps
- **Docker** - Контейнеризация
- **Nginx** - Веб-сервер и прокси

## 📝 API Endpoints

### Видео
- `POST /api/videos/upload` - Загрузка видео
- `GET /api/videos/` - Список видео
- `GET /api/videos/{id}` - Детали видео
- `DELETE /api/videos/{id}` - Удаление видео
- `DELETE /api/videos/{id}/source` - Удалить исходник

### Фрагменты
- `POST /api/videos/{id}/fragments/` - Создать фрагмент
- `GET /api/videos/{id}/fragments/` - Список фрагментов
- `DELETE /api/videos/{id}/fragments/{fragment_id}` - Удалить фрагмент

### Авторизация
- `POST /api/auth/login` - Вход
- `GET /api/auth/captcha` - Получить капчу
- `POST /api/auth/register` - Регистрация

### Поиск
- `POST /api/videos/search` - Поиск видео

### Яндекс.Диск
- `GET /api/yandex/auth-url` - URL для авторизации
- `POST /api/yandex/connect` - Подключить диск
- `GET /api/yandex/status` - Статус подключения

## 🔄 Резервное копирование

База данных и видео хранятся в директории `./data/`. Для бэкапа:

```bash
# Создать архив
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# Восстановить
tar -xzf backup_20240205.tar.gz
```

## ⚙️ Переменные окружения

Создай файл `.env` в директории `backend/`:

```env
DATABASE_URL=sqlite+aiosqlite:///./data/archive.db
SECRET_KEY=your-super-secret-key
YANDEX_CLIENT_ID=your-client-id
YANDEX_CLIENT_SECRET=your-client-secret
UPLOAD_DIR=/app/data/uploads
```

## 🤝 Вклад в проект

1. Fork репозитория
2. Создай feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Открой Pull Request

## 📄 Лицензия

Распространяется под лицензией MIT.

## 👨‍💻 Автор

**samocvetov** - [GitHub](https://github.com/samocvetov)

---

⭐ Если проект полезен, поставь звезду на GitHub!
