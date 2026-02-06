# Production Deployment Guide

## 1. Подготовка сервера

### Минимальные требования:
- Ubuntu 20.04/22.04 или Debian 11+
- 2 CPU, 4 GB RAM
- 50 GB SSD (для видео лучше 100GB+)
- Доменное имя с SSL сертификатом

### Установка зависимостей:
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python
sudo apt install -y python3 python3-pip python3-venv

# Установка FFmpeg
sudo apt install -y ffmpeg

# Установка Nginx
sudo apt install -y nginx

# Установка Node.js (для сборки фронтенда)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Установка Git
sudo apt install -y git
```

## 2. Копирование проекта

```bash
# Создаем директорию
sudo mkdir -p /opt/archive
sudo chown $USER:$USER /opt/archive
cd /opt/archive

# Копируем файлы (через git или scp)
git clone <your-repo> .
# или
scp -r /path/to/local/archive/* user@server:/opt/archive/
```

## 3. Настройка бэкенда

```bash
cd /opt/archive/backend

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Создаем .env файл
cat > .env << EOF
DATABASE_URL=sqlite+aiosqlite:///./archive.db
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=/opt/archive/data/uploads
FRAGMENTS_DIR=/opt/archive/data/uploads/fragments
MAX_UPLOAD_SIZE=2147483648
FFmpeg_PATH=/usr/bin/ffmpeg
EOF

# Создаем директории для данных
mkdir -p /opt/archive/data/uploads/fragments
mkdir -p /opt/archive/data/uploads/thumbnails

# Запускаем миграции
python migrate.py
python migrate_auth.py
python migrate_yandex.py
```

## 4. Настройка systemd сервиса

```bash
sudo tee /etc/systemd/system/archive-backend.service << 'EOF'
[Unit]
Description=Video Archive Backend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/archive/backend
Environment="PATH=/opt/archive/backend/venv/bin"
EnvironmentFile=/opt/archive/backend/.env
ExecStart=/opt/archive/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable archive-backend
sudo systemctl start archive-backend
```

## 5. Сборка фронтенда

```bash
cd /opt/archive/frontend

# Устанавливаем зависимости
npm install

# Создаем production build
npm run build

# Копируем сборку в директорию Nginx
sudo cp -r dist/* /var/www/archive/
sudo chown -R www-data:www-data /var/www/archive
```

## 6. Настройка Nginx

```bash
# Удаляем дефолтный конфиг
sudo rm /etc/nginx/sites-enabled/default

# Создаем конфиг для нашего приложения
sudo tee /etc/nginx/sites-available/archive << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    
    # Frontend (статические файлы)
    location / {
        root /var/www/archive;
        try_files $uri $uri/ /index.html;
        
        # Кэширование статики
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Увеличиваем лимиты для загрузки видео
        client_max_body_size 2G;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
    
    # Static files (видео)
    location /static/ {
        alias /opt/archive/data/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Активируем конфиг
sudo ln -s /etc/nginx/sites-available/archive /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 7. SSL Сертификат (Let's Encrypt)

```bash
# Установка certbot
sudo apt install -y certbot python3-certbot-nginx

# Получаем сертификат
sudo certbot --nginx -d your-domain.com

# Автообновление
sudo systemctl enable certbot.timer
```

## 8. Настройка файрвола

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

## 9. Мониторинг и логи

```bash
# Установка logrotate для ротации логов
sudo tee /etc/logrotate.d/archive << 'EOF'
/opt/archive/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data www-data
}
EOF

# Создаем директорию для логов
sudo mkdir -p /opt/archive/logs
sudo chown www-data:www-data /opt/archive/logs
```

## 10. Резервное копирование

```bash
# Создаем скрипт бэкапа
sudo tee /opt/archive/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/archive/backups"

mkdir -p $BACKUP_DIR

# Бэкап базы данных
cp /opt/archive/backend/archive.db $BACKUP_DIR/archive_$DATE.db

# Бэкап видео
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C /opt/archive/data uploads

# Удаляем старые бэкапы (оставляем последние 7)
ls -t $BACKUP_DIR/archive_*.db | tail -n +8 | xargs -r rm
ls -t $BACKUP_DIR/uploads_*.tar.gz | tail -n +8 | xargs -r rm
EOF

sudo chmod +x /opt/archive/backup.sh

# Добавляем в cron (каждый день в 3 ночи)
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/archive/backup.sh") | crontab -
```

## 11. Проверка работы

```bash
# Проверяем статус сервисов
sudo systemctl status archive-backend
sudo systemctl status nginx

# Проверяем логи
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u archive-backend -f

# Тест API
curl https://your-domain.com/api/health
```

## Docker вариант (альтернатива)

Если предпочитаешь Docker:

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    volumes:
      - ./data:/app/data
      - ./backend:/app
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/archive.db
    restart: always
    
  frontend:
    build: ./frontend
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./data:/var/www/static
    depends_on:
      - backend
    restart: always
```

## Чек-лист перед запуском

- [ ] Домен настроен и ссылается на сервер
- [ ] SSL сертификат установлен
- [ ] Порты 80 и 443 открыты
- [ ] База данных создана и мигрирована
- [ ] Директории для загрузок созданы
- [ ] Systemd сервис активирован
- [ ] Nginx настроен
- [ ] Бэкапы настроены
- [ ] Логи настроены
- [ ] Тестовое видео загружается
- [ ] Фрагменты создаются

## Команды для управления

```bash
# Перезапуск сервиса
sudo systemctl restart archive-backend

# Просмотр логов
sudo journalctl -u archive-backend -f

# Обновление кода
cd /opt/archive && git pull
sudo systemctl restart archive-backend

# Бэкап вручную
sudo /opt/archive/backup.sh
```
