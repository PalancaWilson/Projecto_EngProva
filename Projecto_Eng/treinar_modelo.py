import os
import shutil
import random
from sklearn.model_selection import train_test_split
from ultralytics import YOLO

# Caminhos
DADOS_ORIGINAIS = 'dataset_preparado'
DADOS_DESTINO = 'dataset'
CAMINHO_YAML = 'carros.yaml'

# 1. Criar estrutura de treino e validação
def preparar_dados():
    if os.path.exists(DADOS_DESTINO):
        shutil.rmtree(DADOS_DESTINO)
    os.makedirs(os.path.join(DADOS_DESTINO, 'train'))
    os.makedirs(os.path.join(DADOS_DESTINO, 'val'))

    classes = os.listdir(DADOS_ORIGINAIS)
    classes = [c for c in classes if os.path.isdir(os.path.join(DADOS_ORIGINAIS, c))]

    for classe in classes:
        imagens = os.listdir(os.path.join(DADOS_ORIGINAIS, classe))
        imagens = [img for img in imagens if img.lower().endswith(('.png', '.jpg', '.jpeg'))]

        treino, validacao = train_test_split(imagens, test_size=0.2, random_state=42)

        for tipo, conjunto in [('train', treino), ('val', validacao)]:
            pasta_destino = os.path.join(DADOS_DESTINO, tipo, classe)
            os.makedirs(pasta_destino, exist_ok=True)
            for img in conjunto:
                origem = os.path.join(DADOS_ORIGINAIS, classe, img)
                destino = os.path.join(pasta_destino, img)
                shutil.copy2(origem, destino)

    return classes

# 2. Criar o arquivo carros.yaml
def criar_yaml(classes):
    with open(CAMINHO_YAML, 'w', encoding='utf-8') as f:
        f.write(f"path: {os.path.abspath(DADOS_DESTINO)}\n")
        f.write("train: train\n")
        f.write("val: val\n")
        f.write("names:\n")
        for i, nome in enumerate(classes):
            f.write(f"  {i}: {nome}\n")

# 3. Treinar modelo
def treinar_modelo():
    modelo = YOLO('yolov8n-cls.pt')  # ou yolov8s-cls.pt para mais precisão
    modelo.train(
        data=CAMINHO_YAML,
        epochs=10,
        imgsz=224,
        name='classificacao_carros',
        device='cpu'  # Altere para 'cuda' se tiver GPU
    )

# Execução
if __name__ == '__main__':
    classes = preparar_dados()
    criar_yaml(classes)
    treinar_modelo()
