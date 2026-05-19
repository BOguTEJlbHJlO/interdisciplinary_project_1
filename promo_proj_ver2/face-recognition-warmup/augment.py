"""
Аугментация: генерация дополнительных вариантов из имеющихся фото.
Из каждого фото делаем 5 искусственных вариаций.

Использование: python augment.py
"""
import cv2
import numpy as np
from pathlib import Path


def augment_image(img):
    """Возвращает список из 5 аугментированных вариантов."""
    variants = []
    
    # 1. Чуть ярче
    bright = cv2.convertScaleAbs(img, alpha=1.2, beta=20)
    variants.append(bright)
    
    # 2. Чуть темнее
    dark = cv2.convertScaleAbs(img, alpha=0.8, beta=-20)
    variants.append(dark)
    
    # 3. Зеркальное отражение
    flipped = cv2.flip(img, 1)
    variants.append(flipped)
    
    # 4. Лёгкий поворот вправо
    h, w = img.shape[:2]
    M_right = cv2.getRotationMatrix2D((w/2, h/2), -8, 1.0)
    rotated_r = cv2.warpAffine(img, M_right, (w, h), 
                                borderMode=cv2.BORDER_REPLICATE)
    variants.append(rotated_r)
    
    # 5. Лёгкий поворот влево
    M_left = cv2.getRotationMatrix2D((w/2, h/2), 8, 1.0)
    rotated_l = cv2.warpAffine(img, M_left, (w, h),
                                borderMode=cv2.BORDER_REPLICATE)
    variants.append(rotated_l)
    
    # 6. Размытие (имитация фокуса плохой камеры)
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    variants.append(blurred)
    
    # 7. Шум (имитация плохого освещения)
    noise = np.random.normal(0, 10, img.shape).astype(np.uint8)
    noisy = cv2.add(img, noise)
    variants.append(noisy)
    
    return variants


def main():
    dataset = Path("dataset")
    if not dataset.exists():
        print("❌ Папка dataset/ не найдена!")
        return
    
    total_created = 0
    
    for person_dir in dataset.iterdir():
        if not person_dir.is_dir():
            continue
        
        # Берём только оригиналы (не аугментации)
        originals = [
            f for f in person_dir.glob("*.jpg") 
            if not f.stem.startswith("aug_")
        ] + [
            f for f in person_dir.glob("*.png")
            if not f.stem.startswith("aug_")
        ]
        
        if not originals:
            print(f"⚠️  {person_dir.name}: нет оригинальных фото")
            continue
        
        print(f"🔄 {person_dir.name}: {len(originals)} оригиналов → ", end="")
        
        # Удаляем старые аугментации (если перезапускаем)
        for old_aug in person_dir.glob("aug_*.jpg"):
            old_aug.unlink()
        
        created = 0
        for idx, img_path in enumerate(originals):
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"\n   ⚠️  Не смог прочитать {img_path.name}")
                continue
            
            variants = augment_image(img)
            for v_idx, variant in enumerate(variants):
                out_path = person_dir / f"aug_{idx:02d}_{v_idx}.jpg"
                cv2.imwrite(str(out_path), variant)
                created += 1
        
        total_created += created
        print(f"+{created} аугментаций (всего: {len(originals) + created})")
    
    print(f"\n✅ Создано {total_created} аугментированных фото")
    print(f"   Теперь запусти: python train.py")


if __name__ == "__main__":
    main()