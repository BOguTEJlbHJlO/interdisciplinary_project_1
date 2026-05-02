# ⚙️ ТЗ: Backend Developer (сервер)

## Что делаем как команда

Приложение, которое смотрит на фото со стройки и определяет: есть ли на рабочих каска и жилет. Если кого-то нет — показывает красную рамку и пишет "нарушение".

---

## Что ты делаешь простыми словами

Ты делаешь **сервер** — программу, которая работает 24/7 и отвечает на запросы фронтендеров. Когда пользователь загружает фото:

1. Фронтенд отправляет фото **тебе**
2. Ты **сохраняешь** фото на диск
3. Ты **вызываешь функцию** ML-инженера №2, которая прогоняет фото через модель
4. Ты **сохраняешь результат** в базу данных
5. Ты **отправляешь ответ** обратно фронту

Без тебя фронтенд не может общаться с моделью. Ты — посредник между ними.

---

## 🛠 Инструменты

| Инструмент | Зачем |
|------------|-------|
| **Python 3.10+** | Язык программирования |
| **FastAPI** | Самый простой Python-фреймворк для серверов |
| **Uvicorn** | Программа, которая запускает FastAPI |
| **SQLite** | База данных в виде файла (без настройки) |
| **SQLModel** | Удобная работа с базой |
| **VS Code** или **PyCharm** | Редактор кода |

**Документация:**
- FastAPI: https://fastapi.tiangolo.com (официальный туториал на 100 баллов)
- SQLModel: https://sqlmodel.tiangolo.com

---

## 📋 Конкретные задачи по неделям

### Неделя 1: Подними FastAPI

**Цель:** запустить пустой сервер на своём компе.

```bash
# В корне репозитория
mkdir backend && cd backend
python -m venv venv

# Активация виртуального окружения:
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install fastapi uvicorn python-multipart pillow sqlmodel
```

Создай файл `main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Detector СИЗ API")

# КРИТИЧНО: разрешаем фронту обращаться к нам
# Без этого фронт не сможет делать запросы (CORS-ошибка)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для MVP можно так, в проде нельзя
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "Сервер работает"}
```

Запусти:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Открой в браузере:
- http://localhost:8000 — должен ответить JSON `{"status":"ok",...}`
- http://localhost:8000/docs — **автоматическая документация**, тут можно тестить эндпоинты

---

### Неделя 2: Эндпоинт загрузки фото

**Цель:** научить сервер принимать картинки и сохранять их.

Сначала **на заглушке**, не дожидаясь ML-инженеров.

```python
import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаём папку для загруженных файлов
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/detect")
async def detect_image(file: UploadFile = File(...)):
    # Проверяем что это картинка
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Это не картинка")
    
    # Генерируем уникальный ID для файла
    file_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1]
    file_path = f"{UPLOAD_DIR}/{file_id}.{file_extension}"
    
    # Сохраняем файл на диск
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # ЗАГЛУШКА: пока возвращаем фейковый результат
    # Потом заменим на настоящий вызов модели
    fake_result = {
        "id": file_id,
        "detections": [
            {
                "class": "no_helmet",
                "confidence": 0.9,
                "bbox": [100, 100, 200, 200]
            },
            {
                "class": "helmet",
                "confidence": 0.95,
                "bbox": [300, 80, 380, 180]
            }
        ],
        "violations": 1,
        "total_objects": 2
    }
    return fake_result
```

**Проверь:**
1. Запусти `uvicorn main:app --reload`
2. Открой http://localhost:8000/docs
3. Найди `POST /detect`, нажми "Try it out", выбери файл, нажми Execute
4. Должен прийти JSON с фейковыми данными
5. В папке `uploads/` появился файл — отлично!

---

### Неделя 3: Подключаем настоящую модель

**Цель:** заменить заглушку на реальный вызов модели от ML #2.

Когда ML #2 отдаст тебе свой `detector.py`:

1. Положи его рядом с `main.py` (или в папку `ml_inference/`)
2. Скопируй файл `best.pt` от ML #1 в ту же папку
3. Установи зависимости от ML:
```bash
pip install ultralytics
```

4. Импортируй и используй:

```python
from detector import detect  # импортируем функцию ML #2

@app.post("/detect")
async def detect_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Это не картинка")
    
    file_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1]
    file_path = f"{UPLOAD_DIR}/{file_id}.{file_extension}"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Вызываем настоящую модель!
    result = detect(file_path)
    result["id"] = file_id
    return result
```

Проверь через `/docs` — теперь должны приходить настоящие детекции.

---

### Неделя 4: База данных (SQLite)

**Цель:** сохранять историю всех проверок.

SQLite — это база данных в виде одного файла. Никаких настроек, никаких серверов БД, ничего.

Добавь в `main.py`:

```python
from datetime import datetime
from sqlmodel import SQLModel, Field, create_engine, Session, select
import json


# Модель данных в базе
class Violation(SQLModel, table=True):
    id: str = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.now)
    image_path: str
    violations_count: int
    total_objects: int
    detections_json: str  # храним детекции как JSON-строку


# Создаём подключение к базе
engine = create_engine("sqlite:///app.db")
SQLModel.metadata.create_all(engine)


# Меняем эндпоинт detect, чтобы он сохранял результат
@app.post("/detect")
async def detect_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Это не картинка")
    
    file_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1]
    file_path = f"{UPLOAD_DIR}/{file_id}.{file_extension}"
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Прогоняем через модель
    result = detect(file_path)
    
    # Сохраняем в базу
    with Session(engine) as session:
        violation = Violation(
            id=file_id,
            image_path=file_path,
            violations_count=result.get("violations", 0),
            total_objects=result.get("total_objects", 0),
            detections_json=json.dumps(result.get("detections", []))
        )
        session.add(violation)
        session.commit()
    
    result["id"] = file_id
    return result
```

После запуска появится файл `app.db` — это твоя база данных. **Добавь её в `.gitignore`!**

---

### Неделя 5: Эндпоинт истории

**Цель:** дать фронту возможность показывать историю всех проверок.

```python
from fastapi.responses import FileResponse


@app.get("/history")
def get_history(limit: int = 50):
    """Возвращает список последних проверок"""
    with Session(engine) as session:
        statement = (
            select(Violation)
            .order_by(Violation.timestamp.desc())
            .limit(limit)
        )
        violations = session.exec(statement).all()
        
        return [
            {
                "id": v.id,
                "timestamp": v.timestamp.isoformat(),
                "violations_count": v.violations_count,
                "total_objects": v.total_objects,
                "image_url": f"/image/{v.id}"
            }
            for v in violations
        ]


@app.get("/violations/{violation_id}")
def get_violation_details(violation_id: str):
    """Возвращает детали одной проверки"""
    with Session(engine) as session:
        violation = session.get(Violation, violation_id)
        if not violation:
            raise HTTPException(status_code=404, detail="Не найдено")
        
        return {
            "id": violation.id,
            "timestamp": violation.timestamp.isoformat(),
            "violations_count": violation.violations_count,
            "total_objects": violation.total_objects,
            "detections": json.loads(violation.detections_json),
            "image_url": f"/image/{violation.id}"
        }


@app.get("/image/{file_id}")
def get_image(file_id: str):
    """Возвращает картинку по ID"""
    with Session(engine) as session:
        violation = session.get(Violation, file_id)
        if not violation:
            raise HTTPException(status_code=404, detail="Картинка не найдена")
        return FileResponse(violation.image_path)
```

---

### Неделя 6: Статистика (опционально)

**Цель:** дать фронту цифры для красивого дашборда.

```python
from sqlalchemy import func


@app.get("/stats")
def get_stats():
    """Общая статистика"""
    with Session(engine) as session:
        total_checks = session.exec(
            select(func.count(Violation.id))
        ).one()
        
        total_violations = session.exec(
            select(func.sum(Violation.violations_count))
        ).one() or 0
        
        return {
            "total_checks": total_checks,
            "total_violations": int(total_violations),
            "average_violations_per_check": round(
                total_violations / total_checks, 2
            ) if total_checks > 0 else 0
        }
```

---

### Неделя 7: Обработка ошибок и логирование

**Цель:** чтобы сервер не падал при странных входных данных.

```python
import logging

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.post("/detect")
async def detect_image(file: UploadFile = File(...)):
    logger.info(f"Получен файл: {file.filename}, размер: {file.size}")
    
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Это не картинка")
        
        # Ограничение на размер файла (10 МБ)
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413, 
                detail="Файл слишком большой (макс 10 МБ)"
            )
        
        file_id = str(uuid.uuid4())
        file_extension = file.filename.split(".")[-1]
        file_path = f"{UPLOAD_DIR}/{file_id}.{file_extension}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Файл сохранён: {file_path}")
        
        # Прогоняем через модель
        result = detect(file_path)
        logger.info(f"Детекций: {len(result.get('detections', []))}")
        
        # Сохраняем в БД
        with Session(engine) as session:
            violation = Violation(
                id=file_id,
                image_path=file_path,
                violations_count=result.get("violations", 0),
                total_objects=result.get("total_objects", 0),
                detections_json=json.dumps(result.get("detections", []))
            )
            session.add(violation)
            session.commit()
        
        result["id"] = file_id
        return result
    
    except HTTPException:
        raise  # пробрасываем HTTP-ошибки как есть
    except Exception as e:
        logger.error(f"Ошибка обработки: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка сервера: {str(e)}"
        )
```

---

## 📊 Что должно быть готово в конце

- [ ] Сервер запускается одной командой `uvicorn main:app --reload`
- [ ] Работают эндпоинты:
  - `GET /` — проверка работы
  - `POST /detect` — загрузка фото и детекция
  - `GET /history` — список всех проверок
  - `GET /violations/{id}` — детали одной проверки
  - `GET /image/{id}` — получение картинки
  - `GET /stats` — статистика (опционально)
- [ ] Все запросы сохраняются в `app.db`
- [ ] Файл `requirements.txt`:
  ```
  fastapi==0.111.0
  uvicorn[standard]==0.30.1
  python-multipart==0.0.9
  pillow==10.3.0
  sqlmodel==0.0.18
  ultralytics==8.2.0
  ```
- [ ] README в папке `backend/`:
  ```markdown
  # Backend
  
  ## Установка
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  
  ## Запуск
  uvicorn main:app --reload
  
  Документация будет на http://localhost:8000/docs
  ```

---

## 🎓 Советы по вайбкодингу

- В FastAPI документация генерится сама — открывай `/docs` и проверяй там, не пиши Postman
- Когда дебажишь — кидай в Claude **весь файл `main.py`** и описание ошибки. Не вырезай куски.
- SQLite-файл `app.db` — добавь в `.gitignore`, чтобы не коммитить
- Папку `uploads/` тоже добавь в `.gitignore` (но создай пустой файл `uploads/.gitkeep`)
- Если ошибка `CORS` — проверь `allow_origins=["*"]` в коде
- Если ошибка `Address already in use` — порт 8000 занят. Запусти на другом: `uvicorn main:app --port 8001`

---

## 🤝 С кем ты работаешь

- **ML #2 (Inference)** — он даёт тебе `detector.py`. Договоритесь о формате ответа на 2-й неделе!
- **Frontend Web** — он делает запросы к твоему API. Кидай ему ссылку на `/docs`
- **Frontend Mobile** — то же самое
- **QA/DevOps** — он будет тестить твой API на странных входах. Помоги ему составить чек-лист

---

## 🎯 Ключевые понятия

- **API** (Application Programming Interface) — набор эндпоинтов, через которые программы общаются
- **Эндпоинт** (endpoint) — конкретный URL, на который можно сделать запрос
- **HTTP-методы**:
  - `GET` — получить данные
  - `POST` — отправить данные (например, загрузить файл)
  - `PUT/PATCH` — изменить
  - `DELETE` — удалить
- **CORS** — защита браузера, не даёт сайту делать запросы на чужие сервера. Решается строкой `allow_origins=["*"]`
- **JSON** — формат, в котором данные передаются между фронтом и бэком
- **multipart/form-data** — формат для отправки файлов

Удачи! 🚀
