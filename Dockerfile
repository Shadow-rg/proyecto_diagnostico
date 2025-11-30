# Imagen base ligera con Python
FROM python:3.10-slim

# Instala dependencias necesarias para numpy, pillow y tensorflow
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libatlas-base-dev \
    libblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Carpeta de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . .

# Actualizar pip e instalar dependencias
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn pillow numpy tensorflow-cpu==2.12.0

# Puerto que usará Render
EXPOSE 10000

# Comando para iniciar la app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "10000"]
