"""
Миграция: добавление полей для Yandex Disk в таблицу users
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "archive_new.db"

def migrate():
    """Добавляет поля для Яндекс.Диска в таблицу users"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Добавляем поля для Яндекс.Диска
    fields = [
        ("yandex_disk_token", "TEXT"),
        ("yandex_disk_refresh_token", "TEXT"),
        ("yandex_disk_token_expires", "TIMESTAMP"),
        ("yandex_disk_folder", "TEXT DEFAULT '/archive_videos'")
    ]
    
    for field_name, field_type in fields:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {field_name} {field_type}")
            print(f"Added column: users.{field_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column {field_name} already exists")
            else:
                print(f"Error adding {field_name}: {e}")
    
    conn.commit()
    conn.close()
    
    print("\nMigration completed!")

if __name__ == "__main__":
    migrate()
