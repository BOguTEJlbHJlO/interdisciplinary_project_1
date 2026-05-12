import sys
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

CKPT = "face_id_best.pt"
IMG_SIZE = 224
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

ckpt = torch.load(CKPT, map_location=DEVICE)
class_names = ckpt["classes"]
num_classes = len(class_names)

# Та же архитектура, что при обучении
model = models.resnet18(weights=None)
model.fc = nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(model.fc.in_features, num_classes),
)
model.load_state_dict(ckpt["model_state"])
model.to(DEVICE).eval()

tf = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

def predict(img_path: str, threshold: float = 0.6):
    img = Image.open(img_path).convert("RGB")
    x = tf(img).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        probs = torch.softmax(model(x), dim=1)[0]
    conf, idx = probs.max(0)
    name = class_names[idx.item()]
    if conf.item() < threshold:
        return "unknown", conf.item()
    return name, conf.item()

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "test.jpg"
    name, conf = predict(path)
    print(f"Предсказание: {name} (уверенность: {conf:.2%})")
# python src\face_id_predict.py "C:\Users\MainAccount\Documents\Междисциплинарный проект\interdisciplinary_project_1\promo_project\data\val\person_5\135231.jpg"