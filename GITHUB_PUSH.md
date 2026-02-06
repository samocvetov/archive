# Инструкция по публикации на GitHub

## 1. Подготовка репозитория

Открой терминал в папке `C:\archive` и выполни:

```bash
# Инициализация git
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: Video Archive with Docker support"
```

## 2. Подключение к GitHub

```bash
# Добавление удаленного репозитория
git remote add origin https://github.com/samocvetov/archive.git

# Пуш на GitHub
git branch -M main
git push -u origin main
```

## 3. Если нужен токен для авторизации

GitHub требует Personal Access Token вместо пароля:

1. Зайди на https://github.com/settings/tokens
2. Нажми "Generate new token (classic)"
3. Выбери scope: `repo`
4. Скопируй токен
5. Используй токен как пароль при `git push`

## 4. Альтернативный способ (если не работает HTTPS)

```bash
# Используй GitHub CLI
gh auth login
gh repo create samocvetov/archive --public --source=. --push
```

## 5. Проверка

Открой https://github.com/samocvetov/archive и убедись что все файлы загрузились.

## Важно!

⚠️ **Не пушь эти файлы (они в .gitignore):**
- База данных (`*.db`)
- Загруженные видео (`data/`)
- Переменные окружения (`.env`)
- Node_modules (`frontend/node_modules/`)

После пуша на GitHub любой сможет развернуть проект командой:
```bash
git clone https://github.com/samocvetov/archive.git
cd archive
docker-compose up -d
```
