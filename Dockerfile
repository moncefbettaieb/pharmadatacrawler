FROM python:3.11-slim

WORKDIR /app

# Installer Chromium + Driver + dépendances
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
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
    ca-certificates \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copier votre code
COPY . .

# Installer les dépendances Python (Selenium, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# Utiliser le binaire Chromium et le chromedriver installés
ENV PYTHONPATH="/app"

ENTRYPOINT ["python", "-m"]
CMD ["modules.scrappers.save_sitemaps_links_to_mongo"]