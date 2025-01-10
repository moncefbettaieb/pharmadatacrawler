import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis un fichier spécifique selon l'environnement
APP_ENV = os.getenv("APP_ENV", "dev")  # Par défaut, l'environnement est "dev"
env_file = f".env.{APP_ENV}" if APP_ENV in ["uat", "prod"] else ".env"
load_dotenv()


#l'URL de connexion PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuration PostgreSQL
POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "user": os.getenv("POSTGRES_USER", "your_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "your_password"),
    "dbname": os.getenv("POSTGRES_DB", "your_database"),
}

# Configuration MongoDB
MONGO_CONFIG = {
    "host": os.getenv("MONGO_HOST", "localhost"),
    "port": int(os.getenv("MONGO_PORT", 27017)),
    "username": os.getenv("MONGO_USER", ""),
    "password": os.getenv("MONGO_PASSWORD", ""),
    "database": os.getenv("MONGO_DB", "crawler"),
    "replicaSet": os.getenv("REPLICA_SET", "rs0"),
}

# Configuration des logs
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": os.getenv("LOG_LEVEL", "DEBUG"),
        "handlers": ["console"],
    },
}

# Paramètres de scraping
SCRAPER_CONFIG = {
    "user_agent": os.getenv("SCRAPER_USER_AGENT", "Mozilla/5.0 (compatible; MyScraper/1.0)"),
    "timeout": int(os.getenv("SCRAPER_TIMEOUT", 10)),  # Timeout en secondes
    "retry_attempts": int(os.getenv("SCRAPER_RETRY_ATTEMPTS", 3)),  # Nombre de tentatives en cas d'échec
}

# Planification des tâches (optionnel)
SCHEDULER_CONFIG = {
    "frequency": os.getenv("SCRAPER_FREQUENCY", "daily"),  # Fréquence des exécutions (daily, hourly, etc.)
}

# Autres configurations
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")

# Test de configuration au démarrage
if APP_ENV not in ["dev", "uat", "prod"]:
    raise ValueError(f"Environnement inconnu : {APP_ENV}")