FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les scripts
COPY scripts/ ./scripts/

# Utiliser un argument pour spécifier le script
ARG SCRIPT
CMD ["python", "scripts/scrappers/${SCRIPT}"]
