import cv2
import os
from pathlib import Path

# --- НАСТРОЙКИ (измените при необходимости) ---
VIDEOS_DIR = Path("videos")
FRAMES_DIR = Path("frames")
EXTRACT_EVERY_N_FRAME = 10  # Извлекаем каждый 30-й кадр (при 30 FPS = 1 кадр в секунду)
# -------------------------------------------

# Создаем папку для кадров, если её нет
FRAMES_DIR.mkdir(exist_ok=True, parents=True)

# Находим все видеофайлы в папке
video_extensions = (".mp4", ".avi", ".mov", ".mkv")
video_paths = [p for p in VIDEOS_DIR.glob("*") if p.suffix.lower() in video_extensions]

print(f"Найдено видео: {len(video_paths)}")

for video_path in video_paths:
    cap = cv2.VideoCapture(str(video_path))
    frame_count = 0
    saved_count = 0
    video_name = video_path.stem  # Имя файла без расширения

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Сохраняем каждый EXTRACT_EVERY_N_FRAME-й кадр
        if frame_count % EXTRACT_EVERY_N_FRAME == 0:
            # Создаем уникальное имя файла, включающее имя видео и номер кадра
            frame_filename = FRAMES_DIR / f"{video_name}_frame_{frame_count:06d}.jpg"
            cv2.imwrite(str(frame_filename), frame)
            saved_count += 1
            print(f"Сохранен кадр {frame_count} из {video_path.name}, всего сохранено: {saved_count}")
        
        frame_count += 1
    
    cap.release()
    print(f"Готово для {video_path.name}. Сохранено {saved_count} кадров.")
