FROM python:3.12-slim

WORKDIR /app

# Dependencies installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App-Code kopieren
COPY src/ ./src/
COPY .env.example .env

# Logs-Ordner erstellen
RUN mkdir -p logs

# Unbuffered Python output für bessere Logs
ENV PYTHONUNBUFFERED=1

# App starten
CMD ["python", "src/main.py"]
