# Usar una imagen ligera de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para algunas librerías de Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar los requisitos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación (incluyendo la carpeta static)
COPY . .

# Exponer el puerto de FastAPI
EXPOSE 8000

# Comando para arrancar la API
CMD ["python", "api.py"]
