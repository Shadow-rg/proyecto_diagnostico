# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from PIL import Image
import numpy as np
import base64
import io
import json
import tflite_runtime.interpreter as tflite


app = FastAPI()


# --------------------------
# CARGAR MODELO Y CLASES
# --------------------------
with open("classes.json", "r") as f:
    class_names = json.load(f)

interpreter = tflite.Interpreter(model_path="cultivo_model.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()


# --------------------------
# PETICIÓN DEL CLIENTE
# --------------------------
class DiagnosticRequest(BaseModel):
    image_base64: str  # la imagen
    answers: dict      # tus preguntas extra


# --------------------------
# PROCESAR IMAGEN
# --------------------------
def preprocess_image(base64_string):
    img_bytes = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img).astype(np.float32)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    return img_array


# --------------------------
# ENDPOINT PRINCIPAL
# --------------------------
@app.post("/diagnostic")
def diagnostic(req: DiagnosticRequest):

    img_array = preprocess_image(req.image_base64)

    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    predicted_class = class_names[int(np.argmax(output))]
    confidence = float(np.max(output))

    return {
        "cultivo_detectado": predicted_class,
        "confianza": confidence,
        "answers": req.answers
    }
