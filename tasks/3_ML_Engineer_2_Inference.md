# 🧠 ТЗ: ML Engineer #2 — Подключение модели к серверу

## Что делаем как команда

Приложение, которое смотрит на фото со стройки и определяет: есть ли на рабочих каска и жилет. Если кого-то нет — показывает красную рамку и пишет "нарушение".

---

## Что ты делаешь простыми словами

Первый ML-инженер обучает модель и даёт тебе файл `best.pt`. Этот файл сам по себе — просто куча чисел. Твоя задача — написать **функцию**, которая:
1. Принимает картинку
2. Загружает модель
3. Прогоняет картинку через модель
4. Возвращает понятный ответ в виде JSON: "вот рамки, вот классы, вот сколько нарушений"

Эту твою функцию потом вызовет бэкендер. Ты — мост между ML и бэком.

---

## 🛠 Инструменты

| Инструмент | Зачем |
|------------|-------|
| **Python 3.10+** | Язык программирования |
| **VS Code** или **PyCharm** | Редактор кода |
| **ultralytics** | Та же библиотека, что у первого ML — для запуска модели |
| **Pillow** | Работа с картинками |
| **GitHub** | Хранение кода |

---

## 📋 Конкретные задачи по неделям

### Неделя 1: Установка и первый запуск

**Цель:** убедиться, что у тебя работает любая модель локально.

1. Установи Python 3.10 или новее: https://www.python.org/downloads/
2. Создай папку `ml_inference` в репозитории
3. В терминале:

```bash
cd ml_inference
python -m venv venv

# Активация виртуального окружения:
# На Mac/Linux:
source venv/bin/activate
# На Windows:
venv\Scripts\activate

pip install ultralytics pillow
```

4. Создай файл `test_model.py`:

```python
from ultralytics import YOLO

# Пока используем стандартную модель для теста
model = YOLO('yolov8n.pt')
results = model('https://ultralytics.com/images/bus.jpg')
results[0].show()
print("Работает!")
```

5. Запусти: `python test_model.py`. Если увидел картинку с рамками — всё ок.

---

### Неделя 2: Своя функция детекции

**Цель:** написать функцию, которая принимает картинку и возвращает JSON.

Создай файл `detector.py`:

```python
from ultralytics import YOLO
from pathlib import Path

# Путь к модели от ML #1. Пока используем стандартную, потом заменим
MODEL_PATH = 'yolov8n.pt'

# Загружаем модель ОДИН РАЗ при старте приложения
print("Загружаю модель...")
model = YOLO(MODEL_PATH)
print("Модель загружена!")


def detect(image_path: str) -> dict:
    """
    Детектирует объекты на картинке.
    
    Args:
        image_path: путь к файлу с картинкой
    
    Returns:
        dict с детекциями и количеством нарушений
    """
    # Прогоняем картинку через модель
    results = model(image_path)
    
    # Парсим результаты
    detections = []
    for box in results[0].boxes:
        class_id = int(box.cls)
        class_name = results[0].names[class_id]
        confidence = float(box.conf)
        bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
        
        detections.append({
            "class": class_name,
            "confidence": round(confidence, 2),
            "bbox": [round(x, 1) for x in bbox]
        })
    
    # Считаем нарушения (классы, которые начинаются с "no_")
    violations_count = sum(
        1 for d in detections 
        if d["class"].startswith("no_")
    )
    
    return {
        "detections": detections,
        "violations": violations_count,
        "total_objects": len(detections)
    }


# Тест
if __name__ == "__main__":
    result = detect("test.jpg")
    print(result)
```

Скачай любую тестовую картинку, назови `test.jpg`, положи рядом и запусти `python detector.py`.

---

### Неделя 3: Договариваемся с бэкендером

**Цель:** зафиксировать формат данных, чтобы потом не переделывать.

Сядь с бэкендером (можно в Discord/Telegram-звонке), договоритесь:

**Вариант 1 (рекомендую):** твой код = просто файл `detector.py`. Бэкендер импортирует функцию `detect()` и вызывает её.

```python
# в коде бэкендера:
from detector import detect
result = detect("uploaded_photo.jpg")
```

**Вариант 2:** твой код — отдельный мини-сервер. Бэкендер делает к нему HTTP-запросы. **Для MVP это лишнее усложнение, не делай.**

**Зафиксируй формат ответа в Notion** (чтобы фронтендер тоже знал что ожидать):

```json
{
  "detections": [
    {
      "class": "no_helmet",
      "confidence": 0.87,
      "bbox": [120.5, 50.2, 200.8, 180.1]
    },
    {
      "class": "helmet",
      "confidence": 0.95,
      "bbox": [400.0, 60.5, 480.2, 150.8]
    }
  ],
  "violations": 1,
  "total_objects": 2
}
```

`bbox` — это координаты прямоугольника на картинке: `[левый_верх_x, левый_верх_y, правый_низ_x, правый_низ_y]`. Точка (0,0) — левый верхний угол картинки.

---

### Неделя 4: Подключаем настоящую модель от ML #1

**Цель:** заменить стандартную модель на обученную для касок.

1. Получи файл `best.pt` от ML #1 (через Google Drive или прямо в репо)
2. Положи его в папку `ml_inference/`
3. В `detector.py` поменяй строчку:

```python
MODEL_PATH = 'best.pt'  # вместо 'yolov8n.pt'
```

4. Запусти на тестовой картинке со стройки — теперь должны находиться каски и жилеты, а не автобусы

---

### Неделя 5: Видео (опционально, если успеваешь)

**Цель:** обработать не только фото, но и видео.

Добавь в `detector.py` функцию:

```python
def detect_video(video_path: str) -> dict:
    """
    Детектирует объекты на видео.
    Возвращает агрегированную статистику.
    """
    results = model(video_path, stream=True)  # stream=True для экономии памяти
    
    all_violations = []
    total_frames = 0
    
    for frame_idx, result in enumerate(results):
        total_frames += 1
        for box in result.boxes:
            class_name = result.names[int(box.cls)]
            if class_name.startswith("no_"):
                all_violations.append({
                    "frame": frame_idx,
                    "class": class_name,
                    "confidence": round(float(box.conf), 2)
                })
    
    return {
        "total_frames": total_frames,
        "violations": all_violations,
        "violations_count": len(all_violations)
    }
```

**Если не успеваешь — забей.** Делай только фото, это нормально для MVP.

---

### Неделя 6: Обработка ошибок

**Цель:** чтобы при кривом входе функция не валила весь сервер.

```python
def detect(image_path: str) -> dict:
    """
    Детектирует объекты на картинке.
    """
    try:
        # Проверяем, что файл существует
        if not Path(image_path).exists():
            return {"error": "Файл не найден", "detections": [], "violations": 0}
        
        # Проверяем, что это картинка
        if not image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            return {"error": "Не картинка", "detections": [], "violations": 0}
        
        results = model(image_path)
        
        detections = []
        for box in results[0].boxes:
            class_id = int(box.cls)
            detections.append({
                "class": results[0].names[class_id],
                "confidence": round(float(box.conf), 2),
                "bbox": [round(x, 1) for x in box.xyxy[0].tolist()]
            })
        
        violations_count = sum(1 for d in detections if d["class"].startswith("no_"))
        
        return {
            "detections": detections,
            "violations": violations_count,
            "total_objects": len(detections)
        }
    
    except Exception as e:
        print(f"Ошибка детекции: {e}")
        return {
            "error": str(e),
            "detections": [],
            "violations": 0
        }
```

---

### Неделя 7: Оптимизация (если есть время)

**Если модель медленнее 1-2 секунд на фото** — переведи в формат ONNX, это ускорит:

```python
# Запусти один раз, чтобы получить файл best.onnx
model = YOLO('best.pt')
model.export(format='onnx')

# Потом используй ONNX-версию в detector.py
model = YOLO('best.onnx')
```

**Если работает 1-2 секунды и быстрее** — забей, это нормально для MVP.

---

## 📊 Что должно быть готово в конце

- [ ] Файл `detector.py` с функцией `detect(image_path)`
- [ ] Файл `requirements.txt` со списком библиотек:
  ```
  ultralytics==8.2.0
  pillow==10.3.0
  ```
- [ ] Скрипт `test_detector.py`, который запускает функцию на 5 тестовых картинках
- [ ] README в папке `ml_inference/` с описанием:
  - Как установить (`pip install -r requirements.txt`)
  - Как использовать (пример кода)
  - Какой формат ответа

---

## 🎓 Советы по вайбкодингу

- Кидай в Claude свой `detector.py` целиком и проси добавить функцию — он подставит её в нужный стиль
- Если модель грузится медленно (5+ секунд) — убедись, что грузишь её **один раз при старте** (вне функции `detect`), а не при каждом вызове
- Когда дебажишь — добавляй `print()` в каждом ключевом месте, чтобы видеть что происходит
- Документация ultralytics — твой друг: https://docs.ultralytics.com/modes/predict/

---

## 🤝 С кем ты работаешь

- **ML #1 (Training)** — даёт тебе файл `best.pt`. Если детекция плохая — это к нему, не к тебе
- **Backend** — забирает у тебя функцию `detect()` и встраивает в свой код
- **Frontend** — ему нужно знать формат твоего JSON, чтобы рисовать рамки

---

## 🎯 Ключевые понятия

- **Inference** (инференс) — это запуск модели на новых данных. То, чем ты занимаешься.
- **Bounding box (bbox)** — прямоугольник вокруг объекта на картинке. Координаты: левый-верхний и правый-нижний угол.
- **Confidence** (уверенность) — число от 0 до 1, насколько модель уверена в детекции. 0.5+ — приемлемо, 0.8+ — высокая уверенность.
- **ONNX** — формат для оптимизированной модели, работает быстрее чем `.pt` на CPU.
- **NMS** (Non-Maximum Suppression) — алгоритм, который убирает дублирующиеся рамки вокруг одного объекта. ultralytics делает это автоматом.

Удачи! 🚀
