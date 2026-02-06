"""
Исправление путей к видеофайлам фрагментов - убираем 'uploads/' префикс
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "archive_new.db"

def fix_fragment_paths():
    """Исправляет пути к видеофайлам фрагментов"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Получаем все фрагменты с video_filepath
    cursor.execute("SELECT id, video_filepath FROM fragments WHERE video_filepath IS NOT NULL")
    fragments = cursor.fetchall()
    
    print(f"Found {len(fragments)} fragments with video_filepath")
    
    fixed_count = 0
    for fragment_id, video_filepath in fragments:
        if video_filepath and video_filepath.startswith("uploads/"):
            # Убираем 'uploads/' из начала пути
            new_path = video_filepath.replace("uploads/", "", 1)
            
            cursor.execute(
                "UPDATE fragments SET video_filepath = ? WHERE id = ?",
                (new_path, fragment_id)
            )
            print(f"Fixed fragment {fragment_id}: {video_filepath} -> {new_path}")
            fixed_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\nFixed {fixed_count} fragments")
    print("Done!")

if __name__ == "__main__":
    fix_fragment_paths()
