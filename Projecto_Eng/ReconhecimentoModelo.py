from ultralytics import YOLO
import os

# Caminho para o modelo .pt salvo na pasta 'modelos'
CAMINHO_MODELO = os.path.join("modelos", "yolov8n-cls.pt")

# Carrega o modelo de classificação apenas uma vez
modelo = YOLO(CAMINHO_MODELO)

def detectar_modelo_veiculo(imagem_path):
    """
    Detecta o modelo do veículo a partir da imagem usando o modelo local YOLOv8.
    """
    try:
        resultados = modelo(imagem_path)
        classe_id = resultados[0].probs.top1
        nome_modelo = modelo.names[classe_id]
        return nome_modelo
    except Exception as e:
        print(f"❌ Erro ao detectar modelo do veículo: {e}")
        return None
