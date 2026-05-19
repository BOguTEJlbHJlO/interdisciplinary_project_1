"""
Реал-тайм распознавание лиц через веб-камеру.

Использование: python recognize.py
Управление: Q или ESC — выход
"""
import cv2
import face_recognition
import pickle
import numpy as np
import time
from pathlib import Path
from collections import deque, Counter

# Буфер последних N распознаваний для каждого лица в кадре
recognition_history = deque(maxlen=7)


# Цвета для разных людей (BGR)
COLORS = [
    (0, 255, 100), (255, 100, 0), (255, 0, 200), (0, 200, 255),
    (100, 255, 255), (200, 100, 255), (255, 200, 0), (0, 100, 255),
]


def get_color(name):
    if name == "Unknown":
        return (0, 0, 255)
    return COLORS[hash(name) % len(COLORS)]


def main():
    
    # Загружаем эмбеддинги
    if not Path("embeddings.pkl").exists():
        print("❌ embeddings.pkl не найден! Сначала: python train.py")
        return
    
    with open("embeddings.pkl", "rb") as f:
        data = pickle.load(f)
    
    known_encodings = data["encodings"]
    known_names = data["names"]
    
    print(f"📥 Загружено {len(known_encodings)} эмбеддингов")
    print(f"   Известно: {', '.join(sorted(set(known_names)))}")
    print()
    print("📷 Запускаю камеру... Нажми Q для выхода.")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Не удалось открыть камеру!")
        return
    
    # Параметры
    THRESHOLD = 0.45  # порог распознавания (меньше = строже)
    SCALE = 0.5       # уменьшаем кадр для скорости
    SKIP_FRAMES = 2   # обрабатываем каждый N-й кадр
    
    frame_count = 0
    last_faces = []  # сохраняем результат между кадрами
    fps_history = []
    
    while True:
        loop_start = time.time()
        
        ret, frame = cap.read()
        if not ret:
            continue
        
        frame = cv2.flip(frame, 1)
        
        # Обрабатываем не каждый кадр для скорости
        if frame_count % SKIP_FRAMES == 0:
            small = cv2.resize(frame, (0, 0), fx=SCALE, fy=SCALE)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            
            locations = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, locations)
            
            current_faces = []
            for loc, enc in zip(locations, encodings):
                # Классификация
                distances = face_recognition.face_distance(known_encodings, enc)
                best_idx = int(np.argmin(distances))
                best_dist = float(distances[best_idx])
                
                if best_dist < THRESHOLD:
                    raw_name = known_names[best_idx]
                else:
                    raw_name = "Unknown"
                    
                # Добавляем в историю
                recognition_history.append(raw_name)

                # "Голосуем" — какое имя встречается чаще
                if len(recognition_history) >= 3:
                    most_common, count = Counter(recognition_history).most_common(1)[0]
                    if count >= 3:  # минимум 3 кадра подряд за одно имя
                        name = most_common
                    else:
                        name = "in the process of classification..."
                else:
                    name = raw_name

                # Масштабируем координаты обратно
                top, right, bottom, left = loc
                top = int(top / SCALE)
                right = int(right / SCALE)
                bottom = int(bottom / SCALE)
                left = int(left / SCALE)
                
                current_faces.append({
                    "name": name,
                    "distance": best_dist,   # ← вот это сохраняем
                    "box": (left, top, right, bottom),
                })
            
            last_faces = current_faces
        
        # Рисуем рамки
        for face in last_faces:
            left, top, right, bottom = face["box"]
            if face["name"] != "Unknown":
                label = f'{face["name"]} d={face["distance"]:.2f}'
            else:
                label = "Unknown"
            name = face["name"]
            color = get_color(name)
            
            # Главная рамка
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Декоративные уголки
            cl = 20  # длина уголков
            t = 3   # толщина
            cv2.line(frame, (left, top), (left + cl, top), color, t)
            cv2.line(frame, (left, top), (left, top + cl), color, t)
            cv2.line(frame, (right, top), (right - cl, top), color, t)
            cv2.line(frame, (right, top), (right, top + cl), color, t)
            cv2.line(frame, (left, bottom), (left + cl, bottom), color, t)
            cv2.line(frame, (left, bottom), (left, bottom - cl), color, t)
            cv2.line(frame, (right, bottom), (right - cl, bottom), color, t)
            cv2.line(frame, (right, bottom), (right, bottom - cl), color, t)
            
            # Текст с именем и %
            # Показываем РЕАЛЬНОЕ расстояние — честная метрика
            label = f"{name} d={best_dist:.2f}" if name != "Unknown" else "Unknown"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            
            label_y = top - 10 if top > 30 else bottom + th + 10
            
            # Подложка
            cv2.rectangle(frame,
                          (left, label_y - th - 6),
                          (left + tw + 12, label_y + 6),
                          color, -1)
            cv2.putText(frame, label, (left + 6, label_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # FPS
        loop_time = time.time() - loop_start
        fps = 1 / loop_time if loop_time > 0 else 0
        fps_history.append(fps)
        if len(fps_history) > 30:
            fps_history.pop(0)
        avg_fps = sum(fps_history) / len(fps_history)
        
        # Статус-бар
        overlay = frame.copy()
        cv2.rectangle(overlay, (5, 5), (220, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        cv2.putText(frame, f"FPS: {avg_fps:.1f}", (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Faces: {len(last_faces)}", (15, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Known: {len(set(known_names))}", (15, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imshow("Face Recognition", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        
        frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"\n📊 Средний FPS: {avg_fps:.1f}")


if __name__ == "__main__":
    main()