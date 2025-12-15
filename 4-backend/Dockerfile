FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-it.sh .
RUN dos2unix wait-for-it.sh && chmod +x wait-for-it.sh

COPY . .

EXPOSE 5000

# Ejecuta Flask con gunicorn usando tu app factory
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]