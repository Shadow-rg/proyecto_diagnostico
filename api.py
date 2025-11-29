# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from generate_full_report_v4 import generate_full_agro_report_v4

app = FastAPI()

# Modelo de entrada (lo que Flutter enviará)
class DiagnosticRequest(BaseModel):
    cultivo_detectado: str
    confianza: float
    answers: dict

@app.post("/diagnostic")
def diagnostic(req: DiagnosticRequest):
    reporte = generate_full_agro_report_v4(
        req.cultivo_detectado,
        req.confianza,
        req.answers
    )
    return reporte
