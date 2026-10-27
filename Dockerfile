FROM python:3.12-slim

# Evitar que Python escriba archivos .pyc y activar salida sin buffer para logs limpios
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del proyecto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la aplicación
COPY app/ ./app/

# Exponer el puerto por defecto de FastAPI/Uvicorn
EXPOSE 8000

# Comando de arranque del microservicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]