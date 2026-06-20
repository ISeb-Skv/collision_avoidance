import os
import random
import shutil
from pathlib import Path

FRAMES_DIR = Path("frames")               # папка с исходными изображениями
LABELS_DIR = Path("labels")               # папка с txt-файлами из Label Studio
DATASET_DIR = Path("dataset")
TRAIN_RATIO = 0.8

# Сбор пар (изображение, метка)
images = list(FRAMES_DIR.glob("*.jpg")) + list(FRAMES_DIR.glob("*.png"))
pairs = []
for img in images:
    label_path = LABELS_DIR / f"{img.stem}.txt"
    if label_path.exists():
        pairs.append((img, label_path))
    else:
        matches = list(LABELS_DIR.glob(f"*__{img.stem}.txt"))
        if matches:
            pairs.append((img, matches[0]))
        else:
            print(f"Нет метки для {img.name}")

random.shuffle(pairs)
split_idx = int(len(pairs) * TRAIN_RATIO)
train_pairs = pairs[:split_idx]
val_pairs = pairs[split_idx:]

for split in ['train', 'val']:
    (DATASET_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
    (DATASET_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)

def copy_pairs(pair_list, split):
    for img, lbl in pair_list:
        shutil.copy2(img, DATASET_DIR / "images" / split / img.name)
        new_label_name = img.stem + ".txt"
        shutil.copy2(lbl, DATASET_DIR / "labels" / split / new_label_name)

copy_pairs(train_pairs, 'train')
copy_pairs(val_pairs, 'val')

# Создание data.yaml
data_yaml = {
    'path': str(DATASET_DIR.absolute()),
    'train': 'images/train',
    'val': 'images/val',
    'nc': 4,
    'names': ['robot', 'green_light', 'red_light', 'blue_light']
}
with open(DATASET_DIR / 'data.yaml', 'w') as f:
    import yaml
    yaml.dump(data_yaml, f, sort_keys=False)

print(f"Создано {len(train_pairs)} тренировочных и {len(val_pairs)} валидационных пар")
