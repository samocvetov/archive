"""
Миграция файлов фрагментов и обновление путей в базе данных
"""
import sqlite3
import shutil
from pathlib import Path
import os

# Пути
OLD_FRAGMENTS_DIR = Path(r"C:\archive\backend\static\fragments")
NEW_FRAGMENTS_DIR = Path(r"C:\archive\backend\static\uploads\fragments")
DB_PATH = Path(r"C:\archive\backend\archive_new.db")

def migrate_fragments():
    """Перемещает файлы и обновляет пути в базе"""
    
    # Создаем новую директорию
    NEW_FRAGMENTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Перемещаем все файлы
    if OLD_FRAGMENTS_DIR.exists():
        for file in OLD_FRAGMENTS_DIR.iterdir():
            if file.is_file():
                dest = NEW_FRAGMENTS_DIR / file.name
                shutil.move(str(file), str(dest))
                print(f"Moved: {file.name}")
    
    # Обновляем базу данных - убираем 'fragments/' из начала пути
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, video_filepath FROM fragments WHERE video_filepath IS NOT NULL")
    fragments = cursor.fetchall()
    
    print(f"\nUpdating {len(fragments)} records in database...")
    
    for fragment_id, video_filepath in fragments:
        if video_filepath and video_filepath.startswith("fragments/"):
            # Меняем fragments/filename на uploads/fragments/filename
            new_path = f"uploads/{video_filepath}"
            cursor.execute(
                "UPDATE fragments SET video_filepath = ? WHERE id = ?",
                (new_path, fragment_id)
            )
            print(f"Updated fragment {fragment_id}: {video_filepath} -> {new_path}")
    
    conn.commit()
    conn.close()
    
    print("\nMigration completed!")
    
    # Удаляем старую директорию если она пустая
    if OLD_FRAGMENTS_DIR.exists() and not any(OLD_FRAGMENTS_DIR.iterdir()):
        OLD_FRAGMENTS_DIR.rmdir()
        print("Removed old fragments directory")

if __name__ == "__main__":
    migrate_fragments()
