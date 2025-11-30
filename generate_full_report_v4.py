# generate_full_report_v4.py

from datetime import datetime, timezone

# -----------------------------
# METADATOS DE CULTIVOS (icono, color, nombre)
# -----------------------------
CROP_META = {
    "maize":    {"nombre": "Maíz", "icon": "🌽", "color": "#F4B400"},
    "tomato":   {"nombre": "Tomate", "icon": "🍅", "color": "#DB4437"},
    "rice":     {"nombre": "Arroz", "icon": "🌾", "color": "#C2B280"},
    "wheat":    {"nombre": "Trigo", "icon": "🌾", "color": "#DDB967"},
    "soyabean": {"nombre": "Soya", "icon": "🫘", "color": "#9E9D24"},  # corregido
    "chilli":   {"nombre": "Chile", "icon": "🌶️", "color": "#C62828"},
    "banana":   {"nombre": "Banano", "icon": "🍌", "color": "#FDD835"},
    "coconut":  {"nombre": "Coco", "icon": "🥥", "color": "#8D6E63"},
    "papaya":   {"nombre": "Papaya", "icon": "🥭", "color": "#FFB74D"},
    "no_cultivo": {"nombre": "Sin cultivo", "icon": "❓", "color": "#9E9E9E"}  # añadido
}


# -----------------------------
# Recomendaciones por cultivo (breve + acciones)
# -----------------------------
CROP_RECOMMENDATIONS = {
    "maize": {
        "breve": "Mantener riegos regulares; vigilar orugas y estado nutricional (N).",
        "acciones": [
            "Revisar cogollo y retirar orugas manualmente o aplicar Bacillus thuringiensis (Bt).",
            "Aplicar fertilizante nitrogenado en dosis moderadas si hay clorosis.",
            "Regar temprano en la mañana y evitar encharcamientos."
        ]
    },
    "tomato": {
        "breve": "Evitar mojar hojas; vigilar hongos y plagas como trips y pulgón.",
        "acciones": [
            "Regar a nivel de suelo para no mojar follaje.",
            "Aplicar fungicida y mejorar ventilación si hay manchas en hojas.",
            "Usar trampas cromáticas para trips y control localizado para pulgón."
        ]
    },
    "rice": {
        "breve": "Control de lámina de agua y manejo de malezas.",
        "acciones": [
            "Mantener lámina de agua adecuada según etapa del cultivo.",
            "Control de maleza en etapa temprana.",
            "Evitar estrés por encharcamiento prolongado."
        ]
    },
    "wheat": {
        "breve": "Evitar exceso de humedad en etapas críticas; vigilar roya.",
        "acciones": [
            "Monitorear y aplicar fungicidas preventivos si hay historial.",
            "Evitar el exceso de riego en floración.",
            "Ajustar fertilización en etapas de macollado/espigado."
        ]
    },
    "soyabean": {
        "breve": "Control de chupadores; rotación y balance nutricional.",
        "acciones": [
            "Aplicar control suave contra pulgones (jabón potásico).",
            "Mantener balance de nitrógeno mediante rotación y manejo de suelos.",
            "Monitoreo intenso en floración por plagas defoliadoras."
        ]
    },
    "chilli": {
        "breve": "Ventilación; controlar hongos y proteger fruto.",
        "acciones": [
            "Mejorar ventilación para reducir humedad en hojas.",
            "Aplicar fungicida si hay manchas en hojas o frutos.",
            "Monitoreo de frutos para daño por insectos."
        ]
    },
    "banana": {
        "breve": "Control de Sigatoka y manejo foliar.",
        "acciones": [
            "Eliminar hojas enfermas y aplicar tratamiento contra Sigatoka.",
            "Fertilización balanceada con seguimiento foliar.",
            "Evitar encharcamientos en base del pseudotallo."
        ]
    },
    "coconut": {
        "breve": "Monitoreo de plagas de palma y nutrición foliar.",
        "acciones": [
            "Monitoreo y control de picudos/pulgones específicos.",
            "Aplicar nutrición foliar si se detectan deficiencias.",
            "Riego suplementario en sequías."
        ]
    },
    "papaya": {
        "breve": "Buen drenaje y control de hongos/ácaros.",
        "acciones": [
            "Mejorar drenaje y evitar acumulación de agua.",
            "Control leve de trips/ácaros con jabón potásico.",
            "Proteger frutos y evitar golpes que favorezcan podredumbres."
        ]
    }
}

# Mensaje para no_cultivo
NO_CULTIVO_MSG = {
    "titulo": "No se detectó un cultivo",
    "mensaje": "La imagen no muestra una planta reconocible o está fuera de foco.",
    "accion": "Acérquese al follaje, enfoque la hoja/tallo y evite incluir personas u objetos."
}

# Keys esperadas de las respuestas (UI/CSV)
EXPECTED_ANSWER_KEYS = [
    "edad_dias","estado_fenologico","tipo_suelo","humedad_suelo","ph_suelo",
    "frecuencia_riego","ultima_fertilizacion","tipo_fert","sintoma_visual",
    "severidad","insectos_vistos","temp_ambiente_cat","humedad_relativa_cat",
    "ultima_lluvia","fumigado_reciente","maleza_visible","animales_alrededor"
]

# -----------------------------
# Helpers: normalización y utilidades
# -----------------------------
def _norm(s):
    return "" if s is None else str(s).strip()

def _lower(s):
    return _norm(s).lower()

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

# Mapas de tratamientos por plaga/simple referencia (ejemplos prácticos)
PEST_TREATMENTS = {
    "oruga": {
        "descripcion": "Orugas defoliadoras (p. ej. cogollera en maíz).",
        "tratamiento": [
            "Revisión manual y recolección de orugas en parcelas pequeñas.",
            "Aplicar Bacillus thuringiensis (Bt) para control biológico.",
            "Si es necesario, insecticida recomendado por un técnico (uso responsable)."
        ]
    },
    "pulgon": {
        "descripcion": "Pulgones (insectos chupadores).",
        "tratamiento": [
            "Aplicar jabón potásico o aceite hortícola para control suave.",
            "Introducir control biológico (crisopas, avispas parásitas) si es posible.",
            "Evitar insecticidas sistémicos si no es necesario."
        ]
    },
    "mosquita blanca": {
        "descripcion": "Mosca blanca, transmisora de virus y succión de savia.",
        "tratamiento": [
            "Trampas cromáticas amarillas y control localizado.",
            "Control biológico y manejo cultural."
        ]
    },
    "minador": {
        "descripcion": "Minador de hojas (mina en tejido foliar).",
        "tratamiento": [
            "Retirar hojas muy afectadas.",
            "Aplicar manejo biológico o insecticidas específicos si el daño es extenso."
        ]
    },
    "trips": {
        "descripcion": "Trips (pequeños) afectan flores/hojas y transmiten virus.",
        "tratamiento": [
            "Trampas azules/cromáticas y control localizado.",
            "Control biológico y evitar uso indiscriminado de químicos."
        ]
    }
}

# -----------------------------
# Núcleo: análisis de respuestas con reglas agronómicas
# -----------------------------
def _analyze_answers(answers):
    """
    Interpreta las respuestas y devuelve dict con:
    - parsed (valores normalizados)
    - problemas (lista de strings)
    - acciones (lista de strings recomendadas)
    - gravedad (Bajo/Medio/Alto)
    - notas (info agronómica adicional)
    """
    parsed = {k: _norm(answers.get(k, "")) for k in EXPECTED_ANSWER_KEYS}
    lower = {k: parsed[k].lower() for k in parsed}
    problemas = []
    acciones = []
    notas = []
    gravedad = "Bajo"

    # RIEGO / HUMEDAD
    if lower["frecuencia_riego"] in ["muy poco","sin riego reciente"] or lower["humedad_suelo"] in ["muy seco","seco"]:
        problemas.append("Estrés hídrico")
        acciones.append("Aumentar frecuencia de riego de forma gradual; regar por la mañana o tarde.")
        notas.append("El estrés hídrico reduce la absorción de nutrientes y provoca clorosis.")
        gravedad = "Medio"

    if lower["humedad_suelo"] in ["humedo","encharcado"] or lower["ultima_lluvia"] in ["hoy","esta semana"]:
        # si hay signos visuales compatibles
        if "hongo" in lower["sintoma_visual"] or "mancha" in lower["sintoma_visual"]:
            problemas.append("Riesgo de infección fúngica")
            acciones.append("Mejorar drenaje, evitar riego por aspersión sobre el follaje y considerar fungicida específico.")
            notas.append("Suelos con mal drenaje y follaje húmedo favorecen esporulación de hongos.")
            gravedad = "Medio"

    # PLAGAS
    if lower["insectos_vistos"] in ["oruga","pulgon","mosquita blanca","minador","trips"]:
        insecto = lower["insectos_vistos"]
        problemas.append(f"Plaga detectada: {insecto}")
        # tratamiento específico si tenemos info
        t = PEST_TREATMENTS.get(insecto, None)
        if t:
            acciones += t["tratamiento"]
            notas.append(t["descripcion"])
        else:
            acciones.append("Control localizado: jabón potásico o insecticida recomendado por técnico.")
        gravedad = "Medio"

    # TEMPERATURA Y ESTRÉS TÉRMICO
    if lower["temp_ambiente_cat"] in [">32","26-32"] and ("puntas secas" in lower["sintoma_visual"] or "hojas amarillas" in lower["sintoma_visual"]):
        problemas.append("Estrés por calor")
        acciones.append("Riego en horas frescas y aplicar sombra temporal si es posible.")
        notas.append("Altas temperaturas incrementan demanda evapotranspirativa y provocan marchitez.")
        gravedad = "Medio"

    # NUTRICIÓN SIMPLE (clorosis foliar)
    if "hojas amarillas" in lower["sintoma_visual"] or "clorosis" in lower["sintoma_visual"]:
        problemas.append("Posible deficiencia nutricional (nitrógeno o hierro según patrón)")
        acciones.append("Aplicar fertilizante con N en dosis moderada o realizar análisis foliar para diagnóstico preciso.")
        notas.append("La clorosis generalizada suele indicar deficiencia de nitrógeno; clorosis en nervaduras puede indicar Fe.")
        if gravedad != "Alto":
            gravedad = "Medio"

    # SEVERIDAD REPORTADA
    if lower["severidad"] in ["fuerte","muy fuerte"]:
        gravedad = "Alto"
        notas.append("Severidad reportada por usuario elevada -> acción rápida recomendada.")
    elif lower["severidad"] == "moderada" and gravedad == "Bajo":
        gravedad = "Medio"

    # SI NINGUN PROBLEMA
    if not problemas:
        problemas.append("No se detectan problemas visuales graves")
        acciones.append("Mantener prácticas actuales y monitorear semanalmente.")
        notas.append("Monitoreo regular es clave para detección temprana.")

    # Deduplicar acciones preservando orden
    seen = set()
    acciones_unicas = []
    for a in acciones:
        if a not in seen:
            acciones_unicas.append(a)
            seen.add(a)

    return {
        "parsed": parsed,
        "problemas": problemas,
        "acciones": acciones_unicas,
        "gravedad": gravedad,
        "notas": notas
    }

# -----------------------------
# Generador de texto largo (estilo agrónomo) — explica por qué y cómo
# -----------------------------
def _build_long_text(cultivo_nombre, analysis):
    parsed = analysis["parsed"]
    problemas = analysis["problemas"]
    gravedad = analysis["gravedad"]
    notas = analysis["notas"]

    intro = f"Diagnóstico detallado para {cultivo_nombre}.\n"
    intro += f"Nivel de importancia: {gravedad}.\n\n"

    # Describir contexto
    contexto = []
    if parsed.get("edad_dias"):
        contexto.append(f"Edad aproximada: {parsed['edad_dias']} días")
    if parsed.get("estado_fenologico"):
        contexto.append(f"Estado fenológico: {parsed['estado_fenologico']}")
    if parsed.get("tipo_suelo"):
        contexto.append(f"Tipo de suelo: {parsed['tipo_suelo']}")
    if parsed.get("frecuencia_riego"):
        contexto.append(f"Frecuencia de riego: {parsed['frecuencia_riego']}")
    if parsed.get("ultima_lluvia"):
        contexto.append(f"Última lluvia: {parsed['ultima_lluvia']}")
    if contexto:
        intro += "Contexto reportado: " + "; ".join(contexto) + ".\n\n"

    # Problemas y explicación
    body = "Observaciones y explicaciones:\n"
    for p in problemas:
        body += f"- {p}: "
        # explicación por tipo
        pl = p.lower()
        if "estrés hídrico" in pl:
            body += "La planta muestra signos de falta de agua que pueden reducir el crecimiento y provocar clorosis.\n"
        elif "plaga detectada" in pl:
            insecto = p.split(":")[-1].strip()
            body += f"Se observa presencia de {insecto}. Esto puede causar defoliación y pérdida de rendimiento si no se controla.\n"
        elif "riesgo de infección fúngica" in pl:
            body += "Condiciones de humedad y follaje mojado favorecen el desarrollo de hongos; actúe para reducir humedad en hoja.\n"
        elif "estrés por calor" in pl:
            body += "Altas temperaturas aumentan la demanda de agua y pueden causar quemaduras en puntas y marchitez temporal.\n"
        elif "deficiencia nutricional" in pl:
            body += "Síntomas compatibles con falta de nitrógeno o de micronutrientes; se recomienda confirmación con análisis foliar.\n"
        else:
            body += "Requiere monitoreo y observación para confirmar la causa.\n"

    # Notas técnicas adicionales
    extra = ""
    if notas:
        extra += "\nNotas técnicas:\n"
        for n in notas:
            extra += f"- {n}\n"

    conclusion = "\nRecomendaciones prácticas:\n"
    # sugerir acciones generales a partir del análisis (máximo 6)
    # ya existen en analysis['acciones'] pero las explicamos
    for a in analysis["acciones"][:6]:
        conclusion += f"- {a}\n"

    conclusion += "\nAcciones inmediatas (HOY):\n"
    # elegir hasta 3 acciones concretas
    hoy = []
    if any("plaga" in p.lower() for p in problemas):
        hoy.append("Revisar y aplicar control localizado contra la plaga en las plantas afectadas.")
    if parsed.get("humedad_suelo","").lower() in ["muy seco","seco"] or parsed.get("frecuencia_riego","").lower() in ["muy poco","sin riego reciente"]:
        hoy.append("Regar temprano por la mañana y evaluar respuesta en 24 horas.")
    if any("deficiencia" in p.lower() for p in problemas):
        hoy.append("Aplicar una pequeña prueba localizada de fertilizante nitrogenado y observar respuesta en 3-7 días.")
    # completar con recomendaciones del cultivo si faltan
    # (caller will merge con recomendaciones por cultivo)
    for item in hoy[:3]:
        conclusion += f"1. {item}\n"

    # Ensamblar texto largo
    texto_largo = intro + body + extra + conclusion
    return texto_largo

# -----------------------------
# Función principal (v4)
# -----------------------------
def generate_full_agro_report_v4(cultivo_detectado, confianza, answers):
    """
    Produce un reporte HÍPER-DETALLADO y estructurado.
    - cultivo_detectado: clave (maize, tomato, etc.) o 'no_cultivo'
    - confianza: float 0..1
    - answers: dict con EXPECTED_ANSWER_KEYS
    """
    ts = _now_iso()
    c = (cultivo_detectado or "").lower().strip()
    if c == "" or c == "none":
        c = "no_cultivo"

    # Si no es cultivo o confianza baja
    if c == "no_cultivo" or confianza < 0.60:
        return {
            "timestamp": ts,
            "es_cultivo": False,
            "cultivo_key": None,
            "cultivo_nombre": None,
            "icon": "❓",
            "color": "#9E9E9E",
            "confianza": round(confianza,3),
            "titulo": NO_CULTIVO_MSG["titulo"],
            "mensaje": f"{NO_CULTIVO_MSG['mensaje']} (confianza {confianza:.2f})",
            "accion_sugerida": NO_CULTIVO_MSG["accion"],
            "secciones": [],
            "texto_largo": NO_CULTIVO_MSG["mensaje"]
        }

    # Meta cultivo
    meta = CROP_META.get(c, {"nombre": c.capitalize(), "icon": "🌱", "color": "#4CAF50"})
    cultivo_nombre = meta["nombre"]

    # Analizar respuestas
    analysis = _analyze_answers(answers)

    # Obtener recomendaciones por cultivo y unir
    crop_rec = CROP_RECOMMENDATIONS.get(c, {"breve": "", "acciones": []})
    recomendaciones_unidas = list(dict.fromkeys(crop_rec["acciones"] + analysis["acciones"]))

    # Texto extenso explicativo
    texto_largo = _build_long_text(cultivo_nombre, analysis)

    # Acciones para hoy: priorizar plaga, riego, fertilización (max 3)
    acciones_hoy = []
    if any("plaga" in p.lower() for p in analysis["problemas"]):
        acciones_hoy.append("Revisar manualmente la zona afectada y aplicar control localizado contra la plaga.")
    if analysis["parsed"]["humedad_suelo"].lower() in ["muy seco","seco"] or analysis["parsed"]["frecuencia_riego"].lower() in ["muy poco","sin riego reciente"]:
        acciones_hoy.append("Regar por la mañana y verificar humedad mañana.")
    if any("deficiencia" in p.lower() for p in analysis["problemas"]):
        acciones_hoy.append("Aplicar prueba localizada de fertilizante nitrogenado y observar respuesta en 3–7 días.")
    # completar con recomendaciones por cultivo si faltan
    for r in crop_rec["acciones"]:
        if len(acciones_hoy) >= 3: break
        if r not in acciones_hoy:
            acciones_hoy.append(r)
    # fill if still <3
    idx = 0
    while len(acciones_hoy) < 3 and idx < len(analysis["acciones"]):
        if analysis["acciones"][idx] not in acciones_hoy:
            acciones_hoy.append(analysis["acciones"][idx])
        idx += 1

    # Estructura PRO para UI/PDF/CSV
    reporte = {
        "timestamp": ts,
        "es_cultivo": True,
        "cultivo_key": c,
        "cultivo_nombre": cultivo_nombre,
        "icon": meta["icon"],
        "color": meta["color"],
        "confianza": round(confianza,3),

        "reporte_resumido": {
            "gravedad": analysis["gravedad"],
            "color_gravedad": {"Bajo":"#4CAF50","Medio":"#FFC107","Alto":"#F44336"}.get(analysis["gravedad"], "#FFC107"),
            "problema_principal": analysis["problemas"][0] if analysis["problemas"] else "Ninguno",
            "descripcion_corta": crop_rec["breve"]
        },

        "secciones": [
            {"titulo":"Problemas detectados", "icon":"⚠️", "items": analysis["problemas"]},
            {"titulo":"Recomendaciones combinadas", "icon":"💡", "items": recomendaciones_unidas},
            {"titulo":"Acciones para hoy", "icon":"📌", "items": acciones_hoy}
        ],

        "texto_largo": texto_largo,

        # Campos listos para CSV / export
        "csv": {
            "cultivo": cultivo_nombre,
            "confianza": round(confianza,3),
            "gravedad": analysis["gravedad"],
            "problemas": " | ".join(analysis["problemas"]),
            "recomendaciones": " | ".join(recomendaciones_unidas),
            "acciones_hoy": " | ".join(acciones_hoy),
            "timestamp": ts
        }
    }
    return reporte
