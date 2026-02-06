# Инструкция по восстановлению проекта

## Быстрый старт

### 1. Клонирование/копирование файлов

Скопируй все файлы проекта в директорию `C:\archive\`

### 2. Установка зависимостей

**Бэкенд:**
```bash
cd C:\archive\backend
pip install -r requirements.txt
```

**Фронтенд:**
```bash
cd C:\archive\frontend
npm install
```

### 3. Настройка базы данных

База данных SQLite уже создана (`archive_new.db`). Если нужно пересоздать:

```bash
cd C:\archive\backend
# Удалить старую базу (опционально)
del archive_new.db

# Запустить сервер - база создастся автоматически
uvicorn main:app --reload --port 8000
```

### 4. Создание директорий

Убедись, что существуют директории:
```
C:\archive\backend\static\uploads\fragments\
C:\archive\backend\static\uploads\thumbnails\
```

Сервер создаст их автоматически при запуске.

### 5. Запуск

**Терминал 1 (Бэкенд):**
```bash
cd C:\archive\backend
uvicorn main:app --reload --port 8000
```

**Терминал 2 (Фронтенд):**
```bash
cd C:\archive\frontend
npm run dev
```

### 6. Открытие в браузере

Открой: http://192.168.88.21:3000 (или http://localhost:3000)

## Проверка работоспособности

1. **Главная страница** - должна загрузиться
2. **Загрузка видео** - загрузи тестовое видео
3. **Создание фрагмента** - создай фрагмент (1:00-2:00)
4. **Удаление исходника** - нажми "Удалить исходное видео"
5. **Воспроизведение фрагмента** - фрагмент должен воспроизводиться
6. **Поиск** - найди видео по названию

## Важные файлы

### Конфигурация
- `backend/config.py` - настройки путей и БД
- `backend/.env` - переменные окружения (опционально)

### База данных
- `backend/archive_new.db` - SQLite база данных

### Загруженные файлы
- `backend/static/uploads/` - исходные видео
- `backend/static/uploads/fragments/` - извлеченные фрагменты
- `backend/static/uploads/thumbnails/` - превью

## Решение проблем

### Ошибка "Cannot import module"
```bash
cd C:\archive\backend
# Установи зависимости
pip install fastapi uvicorn sqlalchemy aiosqlite python-magic pydantic-settings
```

### Ошибка 404 при воспроизведении фрагмента
1. Проверь что файлы есть в `static/uploads/fragments/`
2. Проверь пути в базе данных
3. Перезапусти сервер

### Файл заблокирован при удалении
- Используется force режим (5 попыток)
- Закрой все вкладки с видео
- Подожди 10 секунд
- Попробуй снова

## Резервное копирование

**Критичные данные для бэкапа:**
1. `backend/archive_new.db` - база данных
2. `backend/static/uploads/` - все видео и фрагменты
3. `backend/config.py` - конфигурация (опционально)

**Команда для бэкапа:**
```powershell
# Windows PowerShell
Compress-Archive -Path "C:\archive\backend\archive_new.db", "C:\archive\backend\static\uploads" -DestinationPath "backup.zip"
```

## Обновление

При обновлении кода:
1. Останови серверы
2. Сделай бэкап базы
3. Скопируй новые файлы
4. Запусти миграции если есть
5. Перезапусти серверы

## Контакты и поддержка

При проблемах:
1. Проверь логи сервера (консоль uvicorn)
2. Проверь логи браузера (F12 → Console)
3. Обратись к CHANGELOG.md для списка изменений
