from ultralytics import YOLO
import cv2
import pytesseract
import re

model = YOLO("modelos/LP-detection.pt")
PADRAO_MATRICULA = r"[A-Z]{2}-\d{2}-\d{2}-[A-Z]{2}"

def preprocessar_imagem(img):
    # Converte para escala de cinza
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Aumenta contraste
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    # Aplica binarização
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def detectar_matricula(imagem_path):
    img = cv2.imread(imagem_path)
    if img is None:
        return None

    results = model.predict(source=img, conf=0.25, imgsz=640)

    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])
            if cls == 0:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                recorte = img[y1:y2, x1:x2]

                # 🔧 pré-processamento para OCR
                recorte = preprocessar_imagem(recorte)

                texto = pytesseract.image_to_string(
                    recorte,
                    config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                ).strip().upper().replace(" ", "").replace("\n", "").replace(":", "-")

                print("Texto OCR detectado:", texto)

                # Caso OCR já esteja correto
                if re.fullmatch(PADRAO_MATRICULA, texto):
                    return texto

                # Tenta reconstruir se vier colado (ex: LD4817HO → LD-48-17-HO)
                reconstruido = re.fullmatch(r"([A-Z]{2})(\d{2})(\d{2})([A-Z]{2})", texto)
                if reconstruido:
                    return f"{reconstruido[1]}-{reconstruido[2]}-{reconstruido[3]}-{reconstruido[4]}"

    return None

