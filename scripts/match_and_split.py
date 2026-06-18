#!/usr/bin/env python3
import random
import shutil
from pathlib import Path

# === НАСТРОЙКИ ===
PROJECT_ROOT = Path("/home/ilya/collision_avoidance_project")
FRAMES_DIR = PROJECT_ROOT / "frames"
LABELS_DIR = PROJECT_ROOT / "results"   # папка с .txt файлами
DATASET_DIR = PROJECT_ROOT / "dataset"

TRAIN_RATIO = 0.8
# =================

# Создаём папки назначения
TRAIN_IMGS = DATASET_DIR / "images/train"
TRAIN_LABS = DATASET_DIR / "labels/train"
VAL_IMGS = DATASET_DIR / "images/val"
VAL_LABS = DATASET_DIR / "labels/val"

for d in [TRAIN_IMGS, TRAIN_LABS, VAL_IMGS, VAL_LABS]:
    d.mkdir(exist_ok=True, parents=True)

# Находим все изображения
images = list(FRAMES_DIR.glob("*.jpg")) + list(FRAMES_DIR.glob("*.png"))
print(f"Изображений: {len(images)}")

pairs = []
for img in images:
    img_stem = img.stem
    # Ищем .txt, который содержит "__" + img_stem
    pattern = f"*__{img_stem}.txt"
    matches = list(LABELS_DIR.glob(pattern))
    if not matches:
        matches = list(LABELS_DIR.rglob(pattern))
    if matches:
        pairs.append((img, matches[0]))
    else:
        print(f"Нет метки: {img_stem}")

print(f"Найдено пар: {len(pairs)}")
if not pairs:
    exit(1)

# Перемешиваем
random.shuffle(pairs)

# Разделяем
split_idx = int(len(pairs) * TRAIN_RATIO)
train_pairs = pairs[:split_idx]
val_pairs = pairs[split_idx:]

def copy_pair(pair, dest_img_dir, dest_lab_dir):
    img, lab = pair
    # Копируем изображение
    shutil.copy2(img, dest_img_dir / img.name)
    # Копируем метку с новым именем (только базовая часть + .txt)
    new_label_name = img.stem + ".txt"
    shutil.copy2(lab, dest_lab_dir / new_label_name)

for p in train_pairs:
    copy_pair(p, TRAIN_IMGS, TRAIN_LABS)
for p in val_pairs:
    copy_pair(p, VAL_IMGS, VAL_LABS)

print(f"Готово. Train: {len(train_pairs)} пар, Val: {len(val_pairs)} пар")
