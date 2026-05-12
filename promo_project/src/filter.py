import os
import random
import shutil

SOURCE_DIR = r'C:\Users\MainAccount\Downloads\archive\celeba_aligned (1)'
MAPPING_FILE = r'C:\Users\MainAccount\Downloads\archive\Identity_CelebA (2).txt'
DATA_ROOT = r'C:\Users\MainAccount\Documents\Междисциплинарный проект\interdisciplinary_project_1\promo_project\data'

VAL_PER_CLASS = 3
SEED = 42  # для воспроизводимости сплита


def load_mapping(mapping_file):
    """Формат строки: '<row_num> <filename> <person_id>'.
    Первая строка — заголовок, его пропускаем."""
    mapping = {}
    with open(mapping_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.split()
            if len(parts) < 3:
                continue
            # Пропускаем заголовок: вторая колонка не похожа на имя файла
            if not parts[1].lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            filename, person_id = parts[1], parts[2]
            mapping.setdefault(person_id, []).append(filename)
    return mapping


def move_class_photos(target_class, destination_dir, mapping, source_dir=SOURCE_DIR):
    target_class = str(target_class)
    os.makedirs(destination_dir, exist_ok=True)

    filenames = mapping.get(target_class, [])
    if not filenames:
        print(f"Класс {target_class} не найден в разметке.")
        return 0

    count = 0
    for filename in filenames:
        src_path = os.path.join(source_dir, filename)
        dst_path = os.path.join(destination_dir, filename)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            count += 1
        else:
            print(f"Файл {filename} не найден в источнике.")

    print(f"Класс {target_class}: скопировано {count} файлов в {destination_dir}")
    return count


def split_train_val(train_dir, val_dir, n_val=VAL_PER_CLASS, seed=SEED):
    """Переносит n_val случайных файлов из train_dir в val_dir."""
    os.makedirs(val_dir, exist_ok=True)
    files = [f for f in os.listdir(train_dir)
             if os.path.isfile(os.path.join(train_dir, f))]

    if len(files) <= n_val:
        print(f"  В {train_dir} всего {len(files)} файлов — пропускаю сплит.")
        return 0

    rng = random.Random(seed)
    val_files = rng.sample(files, n_val)

    for f in val_files:
        shutil.move(os.path.join(train_dir, f), os.path.join(val_dir, f))

    print(f"  → В val перенесено {n_val} файлов из {train_dir}")
    return n_val


if __name__ == "__main__":
    mapping = load_mapping(MAPPING_FILE)

    # (id_класса, имя_подпапки)
    tasks = [
        (4783, 'person_2'),
        (3005, 'person_3'),
        (4631, 'person_4'),
        (3785, 'person_5'), # 8862 половина в очках, половина - нет 
        (2120, 'person_6'),
        (4991, 'person_7'),
        (9775, 'person_8'),
    ]

    # 1. Копируем фото в train/person_N
    for cls, name in tasks:
        train_dir = os.path.join(DATA_ROOT, 'train', name)
        move_class_photos(cls, train_dir, mapping)

    # 2. Отрезаем по 3 фото в val/person_N
    print("\n--- Разделение train/val ---")
    for _, name in tasks:
        train_dir = os.path.join(DATA_ROOT, 'train', name)
        val_dir = os.path.join(DATA_ROOT, 'val', name)
        # фиксируем разный seed на класс, чтобы выборка была независимой,
        # но при этом воспроизводимой
        split_train_val(train_dir, val_dir, seed=SEED + hash(name) % 1000)

    print("\nГотово.")