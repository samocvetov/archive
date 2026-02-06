"""
Миграция: создание таблиц users и captcha_sessions
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "archive_new.db"

def migrate():
    """Создает таблицы users и captcha_sessions"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Создаем таблицу users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            is_superuser BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    print("Created table: users")
    
    # Создаем таблицу captcha_sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS captcha_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            question VARCHAR(255) NOT NULL,
            answer VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used BOOLEAN DEFAULT 0
        )
    """)
    print("Created table: captcha_sessions")
    
    # Добавляем индексы
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_captcha_session_id ON captcha_sessions(session_id)")
    print("Created indexes")
    
    # Добавляем поле owner_id в videos (nullable, чтобы не сломать существующие записи)
    try:
        cursor.execute("ALTER TABLE videos ADD COLUMN owner_id INTEGER REFERENCES users(id)")
        print("Added column: videos.owner_id")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column owner_id already exists in videos")
        else:
            raise
    
    # Создаем дефолтного пользователя admin (пароль: admin123)
    # Хеш пароля: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6K
    cursor.execute("""
        INSERT OR IGNORE INTO users (id, username, hashed_password, is_active, is_superuser)
        VALUES (1, 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6K', 1, 1)
    """)
    print("Created default user: admin (password: admin123)")
    
    conn.commit()
    conn.close()
    print("\nMigration completed successfully!")
    print("\nDefault credentials:")
    print("Username: admin")
    print("Password: admin123")

if __name__ == "__main__":
    migrate()
