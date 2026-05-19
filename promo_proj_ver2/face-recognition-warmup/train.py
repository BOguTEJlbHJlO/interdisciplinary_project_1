"""
Генерация эмбеддингов для всех людей в dataset/.

Использование: python train.py
"""
import face_recognition
import pickle
import time
from pathlib import Path


def main():
    dataset_path = Path("dataset")
    
    if not dataset_path.exists() or not any(dataset_path.iterdir()):
        print("❌ Папка dataset/ пуста! Сначала собери фото через capture.py")
        return
    
    known_encodings = []
    known_names = []
    stats = {}
    
    people = sorted([p for p in dataset_path.iterdir() if p.is_dir()])
    
    print(f"📂 Найдено людей: {len(people)}")
    print(f"   ({', '.join(p.name for p in people)})")
    print()
    
    start = time.time()
    
    for person_dir in people:
        name = person_dir.name
        images = sorted(person_dir.glob("*.jpg")) + sorted(person_dir.glob("*.png"))
        
        if not images:
            print(f"⚠️  {name}: нет фото, пропускаем")
            continue
        
        print(f"🔍 {name}: {len(images)} фото...", end=" ", flush=True)
        success = 0
        
        for image_path in images:
            try:
                image = face_recognition.load_image_file(str(image_path))
                locations = face_recognition.face_locations(image, model="hog")
                
                if not locations:
                    continue
                
                # Если несколько лиц — берём самое большое
                if len(locations) > 1:
                    locations.sort(
                        key=lambda loc: (loc[2] - loc[0]) * (loc[1] - loc[3]),
                        reverse=True
                    )
                    locations = [locations[0]]
                
                encodings = face_recognition.face_encodings(image, locations)
                if encodings:
                    known_encodings.append(encodings[0])
                    known_names.append(name)
                    success += 1
            except Exception as e:
                print(f"\n   ⚠️  Ошибка на {image_path.name}: {e}")
        
        stats[name] = success
        print(f"✅ {success}/{len(images)}")
    
    elapsed = time.time() - start
    
    print()
    print("=" * 50)
    print(f"📊 Итого:")
    print(f"   Эмбеддингов: {len(known_encodings)}")
    print(f"   Людей: {len(stats)}")
    print(f"   Время: {elapsed:.1f}s")
    print()
    
    for name, count in stats.items():
        emoji = "✅" if count >= 5 else "⚠️ "
        print(f"   {emoji} {name}: {count} эмбеддингов")
    
    # Сохраняем
    with open("embeddings.pkl", "wb") as f:
        pickle.dump({"encodings": known_encodings, "names": known_names}, f)
    
    print(f"\n💾 Сохранено в embeddings.pkl")


if __name__ == "__main__":
    main()
#4 минуты 38 секунд обучение, 1.5 минуты на 40 адекватных фоток