"""
Сбор фото лица через камеру.

Использование:
    python capture.py Vasya
    python capture.py Vasya 20  (если хочешь больше фото)

SPACE — снимок, ESC — выход.
"""
import cv2
import os
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Использование: python capture.py <Имя> [количество]")
        print("Пример: python capture.py Vasya 15")
        return
    
    name = sys.argv[1]
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    
    # Папка для фото
    out_dir = Path("dataset") / name
    out_dir.mkdir(parents=True, exist_ok=True)
    
    existing = len(list(out_dir.glob("*.jpg")))
    next_idx = existing + 1
    
    print(f"📸 Запись фото для: {name}")
    print(f"📂 Папка: {out_dir.absolute()}")
    print(f"📊 Уже есть: {existing} фото, цель: {target}")
    print()
    print("SPACE — снимок, ESC — выход")
    print()
    
    # Открываем камеру
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Не удалось открыть камеру!")
        print("   Попробуй закрыть Zoom/Teams/Skype")
        return
    
    # Детектор лиц для подсветки
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    captured = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Зеркалим как зеркало
        frame = cv2.flip(frame, 1)
        display = frame.copy()
        
        # Ищем лица для отображения
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        face_found = len(faces) > 0
        
        for (x, y, w, h) in faces:
            cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Информация на экране
        cv2.putText(display, f"{name}: {captured}/{target}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        if not face_found:
            cv2.putText(display, "Lico ne naydeno!", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv2.putText(display, "Press SPACE", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow(f"Capture: {name}", display)
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            break
        
        if key == 32:  # SPACE
            if not face_found:
                print("⚠️  Лицо не найдено, кадр пропущен")
                continue
            
            filename = out_dir / f"{next_idx:02d}.jpg"
            cv2.imwrite(str(filename), frame)
            captured += 1
            next_idx += 1
            print(f"✅ {filename.name}")
            
            if captured >= target:
                print(f"🎉 Готово! {target} фото для {name}")
                break
    
    cap.release()
    cv2.destroyAllWindows()
    
    total = len(list(out_dir.glob("*.jpg")))
    print(f"\n📊 Всего у {name}: {total} фото")


if __name__ == "__main__":
    main()