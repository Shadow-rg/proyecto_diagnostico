from fastapi import FastAPI
from pydantic import BaseModel
from generate_full_report_v4 import generate_full_agro_report_v4
import numpy as np
from PIL import Image
import base64
import io
import tensorflow as tf  # Usamos TensorFlow en lugar de tflite_runtime

app = FastAPI()

# Cargar modelo TFLite con TensorFlow
interpreter = tf.lite.Interpreter(model_path="modelo_agro.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Lista de clases (de tu classes.json)
class_names = ["banana","chilli","coconut","maize","no_cultivo","papaya","rice","soyabean","tomato","wheat"]

class DiagnosticRequest(BaseModel):
    imageBase64: str
    answers: dict

@app.post("/diagnostic")
def diagnostic(req: DiagnosticRequest):
    try:
        # Decodificar imagen
        image_data = base64.b64decode(req.imageBase64)
        img = Image.open(io.BytesIO(image_data)).convert("RGB").resize((224,224))
        arr = np.array(img).astype("float32") / 255.0
        arr = np.expand_dims(arr, axis=0)

        # Asegurar formato correcto para TFLite
        arr = arr.astype(input_details[0]['dtype'])
        interpreter.set_tensor(input_details[0]['index'], arr)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])[0]

        # Obtener clase y confianza
        idx = int(np.argmax(output_data))
        confianza = float(output_data[idx])
        cultivo_detectado = class_names[idx]

        # Generar reporte
        reporte = generate_full_agro_report_v4(cultivo_detectado, confianza, req.answers)
        return reporte

    except Exception as e:
        return {"error": f"Error al procesar imagen o ejecutar modelo: {str(e)}"}
