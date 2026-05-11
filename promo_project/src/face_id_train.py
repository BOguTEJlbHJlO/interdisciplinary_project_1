"""
Идентификатор лиц на 8 классов
Transfer learning на ResNet18 (ImageNet weights)
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from pathlib import Path

# ---------- Конфиг ----------
DATA_DIR = "dataset"
NUM_CLASSES = 8
BATCH_SIZE = 32
EPOCHS = 20
LR = 1e-3
IMG_SIZE = 224
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------- Аугментации ----------
# Нормализация под ImageNet (используем предобученную сеть)
imagenet_mean = [0.485, 0.456, 0.406]
imagenet_std = [0.229, 0.224, 0.225]

train_tf = transforms.Compose([
    transforms.Resize((IMG_SIZE + 32, IMG_SIZE + 32)),
    transforms.RandomCrop(IMG_SIZE),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.RandomRotation(10),
    transforms.ToTensor(),
    transforms.Normalize(imagenet_mean, imagenet_std),
])

val_tf = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(imagenet_mean, imagenet_std),
])

# ---------- Данные ----------
train_ds = datasets.ImageFolder(f"{DATA_DIR}/train", transform=train_tf)
val_ds = datasets.ImageFolder(f"{DATA_DIR}/val", transform=val_tf)

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)
val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

print(f"Классы: {train_ds.classes}")
print(f"Train: {len(train_ds)} | Val: {len(val_ds)}")

# Сохраняем маппинг класс -> индекс для инференса
class_names = train_ds.classes

# ---------- Модель ----------
def build_model(num_classes: int) -> nn.Module:
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    # Замораживаем все слои кроме последнего блока + классификатора
    for param in model.parameters():
        param.requires_grad = False
    for param in model.layer4.parameters():
        param.requires_grad = True
    # Заменяем head под 8 классов
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, num_classes),
    )
    return model

model = build_model(NUM_CLASSES).to(DEVICE)

criterion = nn.CrossEntropyLoss()
# Оптимизируем только разморожённые параметры
trainable = [p for p in model.parameters() if p.requires_grad]
optimizer = optim.Adam(trainable, lr=LR)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.5)

# ---------- Циклы train/eval ----------
def run_epoch(loader, train: bool):
    model.train() if train else model.eval()
    total_loss, correct, total = 0.0, 0, 0
    ctx = torch.enable_grad() if train else torch.no_grad()
    with ctx:
        for x, y in loader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            logits = model(x)
            loss = criterion(logits, y)
            if train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            total_loss += loss.item() * x.size(0)
            correct += (logits.argmax(1) == y).sum().item()
            total += x.size(0)
    return total_loss / total, correct / total

# ---------- Тренировка ----------
best_acc = 0.0
for epoch in range(1, EPOCHS + 1):
    tr_loss, tr_acc = run_epoch(train_loader, train=True)
    va_loss, va_acc = run_epoch(val_loader, train=False)
    scheduler.step()
    print(f"Epoch {epoch:02d} | train_loss={tr_loss:.4f} acc={tr_acc:.3f} "
          f"| val_loss={va_loss:.4f} acc={va_acc:.3f}")
    if va_acc > best_acc:
        best_acc = va_acc
        torch.save({
            "model_state": model.state_dict(),
            "classes": class_names,
        }, "face_id_best.pt")
        print(f"  -> Сохранил чекпойнт (val_acc={va_acc:.3f})")

print(f"\nЛучшая val accuracy: {best_acc:.3f}")
