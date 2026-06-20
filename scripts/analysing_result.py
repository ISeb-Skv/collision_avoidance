import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import re

RESULTS_DIR = Path("results")
LOGS_DIR = RESULTS_DIR / "logs"

def extract_suffix(video_name):
    match = re.search(r'(\d{6})$', video_name)
    return match.group(1) if match else video_name
all_dfs = []
for csv_file in LOGS_DIR.glob("*.csv"):
    df = pd.read_csv(csv_file)
    video_name = csv_file.stem.replace('log_', '')
    suffix = extract_suffix(video_name)
    df['video'] = suffix
    all_dfs.append(df)
    print(f"Загружен: {csv_file.name} -> видео {suffix}")

if not all_dfs:
    raise FileNotFoundError("Нет CSV-файлов в папке results/logs. Сначала запустите программу 1.")

full_df = pd.concat(all_dfs, ignore_index=True)
print(f"\nВсего записей: {len(full_df)}")

print("\n=== Распределение состояний (по всем видео) ===")
state_counts = full_df['state'].value_counts(normalize=True)
print(state_counts)

plt.figure(figsize=(10,8))
plt.hist2d(full_df['x'], full_df['y'], bins=50, cmap='hot')
plt.colorbar(label='Количество посещений')
plt.title('Тепловая карта траектории машинки (все видео)')
plt.xlabel('X (пиксели)')
plt.ylabel('Y (пиксели)')
plt.savefig(RESULTS_DIR / 'heatmap_trajectory.png', dpi=150)
plt.show()
print(f"Тепловая карта сохранена: {RESULTS_DIR / 'heatmap_trajectory.png'}")

COLLISION_WIDTH_THRESHOLD_PX = 175

for suffix, group in full_df.groupby('video'):
    plt.figure(figsize=(15,5))
    plt.plot(group['frame'], group['width'], label='Ширина (px)', linewidth=1)
    plt.axhline(y=COLLISION_WIDTH_THRESHOLD_PX, color='r', linestyle='--',
                label=f'Порог столкновения ({COLLISION_WIDTH_THRESHOLD_PX} px)')
    plt.title(f'Динамика ширины для видео {suffix}')
    plt.xlabel('Кадр')
    plt.ylabel('Ширина (пиксели)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plot_path = RESULTS_DIR / f'width_dynamics_{suffix}.png'
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"График для видео {suffix} сохранён: {plot_path}")

print("\nАнализ завершён. Все графики сохранены в папку results/.")
