FROM python:3.10-slim

WORKDIR /app

# 1. Instalar herramientas de compilación y dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Copiar requerimientos e instalar paquetes Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. INSTALACIÓN DE PLAYWRIGHT (Browsers)
# Instalamos solo Chromium para ahorrar espacio y sus dependencias de SO
RUN playwright install chromium
RUN playwright install-deps chromium

# 4. Copiar código fuente
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
