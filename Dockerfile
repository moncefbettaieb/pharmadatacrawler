FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    unzip \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxss1 \
    libnss3 \
    libgbm1 \
    libu2f-udev \
    libxtst6 \
    chromium \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH="/app"

ENTRYPOINT ["python", "-m"]
CMD ["scrappers.save_sitemaps_links_to_mongo"]