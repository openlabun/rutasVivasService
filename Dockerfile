# Imagen base más liviana
FROM python:3.11-slim

# Evita archivos .pyc y salida bufferizada
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema requeridas por GDAL y psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    binutils \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Variables de entorno para GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copia solo requirements para instalar antes (optimiza cache Docker)
COPY requirements.txt .

# Instala dependencias de Python sin cache
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
