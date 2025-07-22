# baixar_modelo.py
from ultralytics import YOLO

# Isso vai baixar e armazenar o modelo em cache local
model = YOLO('yolov8n-cls.pt')
print("✅ Modelo YOLOv8n-cls.pt baixado com sucesso.")
