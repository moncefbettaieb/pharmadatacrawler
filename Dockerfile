FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-liberation \
    gnupg \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgbm1 \
    libgtk-3-0 \
    libnss3 \
    libu2f-udev \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxss1 \
    libxtst6 \
    unzip \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# Copy necessary files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add the root folder to PYTHONPATH
ENV PYTHONPATH="/app"

# Default command
ENTRYPOINT ["python", "-m"]
CMD ["scrappers.save_sitemaps_links_to_mongo"]