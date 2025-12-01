# api.py

from fastapi import FastAPI
from pydantic import BaseModel
import tensorflow as tf
import numpy as np
from PIL import Image
import base64
import json

# Cargar clases
with open("classes.json", "r") as f:
    class_names = json.load(f)

# Cargar modelo TFLite
interpreter = tf.lite.Interpreter(model_path="cultivo_model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def predict_image(base64_img):
    image_bytes = base64.b64decode(base64_img)
    img = Image.open(io.BytesIO(image_bytes)).resize((224,224))
    img = np.array(img).astype(np.float32)
    img = np.expand_dims(img, axis=0)

    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()

    output = interpreter.get_tensor(output_details[0]['index'])
    pred_idx = np.argmax(output)

    return class_names[pred_idx], float(np.max(output))

class DiagnosticRequest(BaseModel):
    imageBase64: str

app = FastAPI()

@app.post("/predict")
def predict(req: DiagnosticRequest):
    clase, conf = predict_image(req.imageBase64)
    return {
        "cultivo_detectado": clase,
        "confianza": conf
    }
