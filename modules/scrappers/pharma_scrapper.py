
import sys
import logging
import logging.config
from datetime import datetime
from utils.config import settings
from utils.db.MongoConnection import MongoConnection
from modules.scrappers import pharma_gdd_scraper
from modules.scrappers import pharmacie_du_centre_scrapper

def process_sitemap_entries(driver, db, last_execution=None):
    """
    Traiter les entrées de la collection `sitemaps` en fonction de last_execution.
    """
    sitemaps_collection = db["sitemaps"]
    if driver is None:
        driver = settings.configure_selenium()
    if db is None:
        db = MongoConnection.get_instance()
    for sitemap_entry in sitemaps_collection.find():
        loc = sitemap_entry.get("loc")
        lastmod = sitemap_entry.get("lastmod")
        source = sitemap_entry.get("source")

        if loc is None or source is None:
            print(f"Skipping invalid sitemap entry: {sitemap_entry}")
            continue

        lastmod_date = datetime.strptime(lastmod, "%Y-%m-%d") if lastmod else None

        if last_execution is not None and lastmod_date and lastmod_date <= last_execution:
            print(f"Skipping {loc}, lastmod {lastmod_date} <= last_execution {last_execution}")
            continue

        try:
            print(f"Processing {loc}")
            match source:
                case "pharma-gdd":
                    scraped_data = pharma_gdd_scraper.scrape_pharma_gdd(driver, loc)
                case "pharmacie-du-centre":
                    scraped_data = pharmacie_du_centre_scrapper.scrape_pharma_du_centre(driver, loc)
            for item in scraped_data:
                if item is not None: 
                    item["source"] = source
                insert_scraped_data(source, scraped_data, db, last_execution)

            print(f"Inserted {len(scraped_data)} items from {loc} into {source}")

        except Exception as e:
            print(f"Error processing {loc}: {e}")

def insert_scraped_data(source, data, db, last_execution=None):
    """
    Insérer les données dans la collection MongoDB avec des champs supplémentaires.
    """
    collection = db[source]
    for item in data:
        if item is not None:
            item["processed_time"] = datetime.now()
        collection.insert_one(item)

if __name__ == "__main__":
    logging.config.fileConfig('utils/config/logging.conf')
    logger = logging.getLogger('Pharma Data')
    logger.info(f"Application Started Environnement : {settings.APP_ENV}.")
    db = MongoConnection.get_instance()
    driver = settings.configure_selenium()
    last_execution_arg = sys.argv[1] if len(sys.argv) > 1 else None
    last_execution = (
        datetime.strptime(last_execution_arg, "%Y-%m-%d") if last_execution_arg else None
    )
    logger.info(f"Last execution was at : {last_execution}.")
    try:
        process_sitemap_entries(driver, db, last_execution)
    except Exception as e:
        logger.error(f"Erreur lors du traitement des entrées de sitemap : {e}")
    finally:
        logger.error(f"quit driver")
        driver.quit()
    logger.info("Application terminée.")