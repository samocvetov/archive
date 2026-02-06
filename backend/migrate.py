"""
Миграция базы данных: добавление полей video_filepath и video_file_size в таблицу fragments
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "archive_new.db"

def migrate():
    """Добавляет новые колонки в таблицу fragments"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Проверяем существование колонок
    cursor.execute("PRAGMA table_info(fragments)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"Current columns: {column_names}")
    
    # Добавляем video_filepath если не существует
    if 'video_filepath' not in column_names:
        print("Adding video_filepath column...")
        cursor.execute("ALTER TABLE fragments ADD COLUMN video_filepath TEXT")
        conn.commit()
        print("OK: video_filepath column added")
    else:
        print("video_filepath column already exists")
    
    # Добавляем video_file_size если не существует
    if 'video_file_size' not in column_names:
        print("Adding video_file_size column...")
        cursor.execute("ALTER TABLE fragments ADD COLUMN video_file_size INTEGER")
        conn.commit()
        print("OK: video_file_size column added")
    else:
        print("video_file_size column already exists")
    
    conn.close()
    print("\nMigration completed!")

if __name__ == "__main__":
    migrate()
