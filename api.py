# api.py
from fastapi import FastAPI, UploadFile, File
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import json
import io
from PIL import Image

app = FastAPI()

# ================================
# CARGAR MODELO TFLITE
# ================================
interpreter = tf.lite.Interpreter(model_path="cultivo_model.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Cargar nombres de clases
with open("classes.json", "r") as f:
    class_names = json.load(f)


# ================================
# FUNCIÓN PARA PROCESAR IMAGEN
# ================================
def preprocess_image(uploaded_file):

    img = Image.open(uploaded_file).convert("RGB")
    img = img.resize((224, 224))

    img_array = np.array(img).astype(np.float32)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # normalización igual que en Colab

    return img_array


# ================================
# ENDPOINT PRINCIPAL
# ================================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    # Leer archivo
    content = await file.read()
    img = preprocess_image(io.BytesIO(content))

    # Mandar al modelo
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()

    # Obtener predicción
    output_data = interpreter.get_tensor(output_details[0]['index'])
    class_index = int(np.argmax(output_data))
    predicted_class = class_names[class_index]
    confidence = float(np.max(output_data))

    return {
        "cultivo_detectado": predicted_class,
        "confianza": confidence,
    }


# ================================
# ENDPOINT OPCIONAL PARA APP
# CON REPORTE AUTOMÁTICO
# ================================
from generate_full_report_v4 import generate_full_agro_report_v4
from pydantic import BaseModel

class DiagnosticRequest(BaseModel):
    answers: dict
    cultivo_detectado: str
    confianza: float

@app.post("/diagnostic")
def diagnostic(req: DiagnosticRequest):
    reporte = generate_full_agro_report_v4(
        req.cultivo_detectado,
        req.confianza,
        req.answers
    )
    return reporte
