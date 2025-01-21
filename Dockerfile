FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libgbm1 \
    libu2f-udev \
    libxtst6 \
    && apt-get clean

# Installer Chrome
RUN apt -f install -y
RUN apt-get install -y wget
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install ./google-chrome-stable_current_amd64.deb -y

# Copier les fichiers nécessaires
COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Ajouter le dossier racine au PYTHONPATH
ENV PYTHONPATH="/app"

# Commande par défaut
ENTRYPOINT ["python", "-m"]
CMD ["scrappers.save_sitemaps_links_to_mongo"]
