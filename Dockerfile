# Imagen base
FROM python:3.11

# Evita archivos .pyc y salida bufferizada
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crea y define el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias para psycopg2 y otros paquetes
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    binutils \
    gdal-bin \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de dependencias
COPY requirements.txt .

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de tu proyecto al contenedor
COPY . .

# Ejecuta los comandos de Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
