from fastapi import FastAPI
from pydantic import BaseModel
from generate_full_report_v4 import generate_full_agro_report_v4
import numpy as np
from PIL import Image
import base64
import io
import json
import tensorflow as tf  # Usamos TensorFlow para cargar el modelo TFLite

app = FastAPI()

# Cargar modelo TFLite con TensorFlow
interpreter = tf.lite.Interpreter(model_path="modelo_agro.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Cargar clases desde archivo JSON (asegura orden correcto)
with open("classes.json", "r") as f:
    class_names = json.load(f)

class DiagnosticRequest(BaseModel):
    imageBase64: str
    answers: dict

@app.post("/diagnostic")
def diagnostic(req: DiagnosticRequest):
    try:
        # Decodificar imagen desde Base64
        image_data = base64.b64decode(req.imageBase64)
        img = Image.open(io.BytesIO(image_data)).convert("RGB").resize((224,224))

        # Preprocesamiento idéntico al entrenamiento
        arr = np.array(img).astype("float32") / 255.0
        arr = np.expand_dims(arr, axis=0)

        # Pasar al modelo
        interpreter.set_tensor(input_details[0]['index'], arr)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])[0]

        # Obtener clase y confianza
        idx = int(np.argmax(output_data))
        confianza = float(output_data[idx])
        cultivo_detectado = class_names[idx]

        # 🔍 DEBUG opcional: imprimir probabilidades
        print("🔢 Probabilidades:", output_data.tolist())
        print("✅ Cultivo detectado:", cultivo_detectado)

        # Generar reporte con tu función
        reporte = generate_full_agro_report_v4(cultivo_detectado, confianza, req.answers)
        return reporte

    except Exception as e:
        return {"error": f"Error al procesar imagen o ejecutar modelo: {str(e)}"}
