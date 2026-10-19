# Imagen base: Linux mínimo con Python 3.12
FROM python:3.12-slim

# Muestra los print() al instante en los registros
ENV PYTHONUNBUFFERED=1

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Se copia primero requirements.txt para aprovechar la caché de capas
COPY requirements.txt .

# Instala las librerías sin guardar archivos temporales
RUN pip install --no-cache-dir -r requirements.txt

# Ahora sí, el script
COPY agente_soporte.py .

# Comando que corre al arrancar el contenedor
ENTRYPOINT ["python", "agente_soporte.py"]