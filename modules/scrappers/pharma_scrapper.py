
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
    logger.info(f"Last execution was at : {last_execution}.")
    if last_execution is not None  or last_execution != "None":
        last_execution_dt = datetime.strptime(last_execution, "%d-%m-%Y")
        items = sitemaps_collection.find({
            "lastmod": {
            "$gt": last_execution_dt.strftime("%Y-%m-%d")
            }
        })
        doc_count = sitemaps_collection.count_documents({
            "lastmod": {
            "$gt": last_execution_dt.strftime("%Y-%m-%d")
            }
        })
        print(f"Processing {doc_count} items since {last_execution}")
    else:
        items = sitemaps_collection.find()
    
    for sitemap_entry in items:
        loc = sitemap_entry.get("loc")
        source = sitemap_entry.get("source")

        if loc is None or source is None:
            print(f"Skipping invalid sitemap entry: {sitemap_entry}")
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
                insert_scraped_data(source.replace('-','_'), scraped_data, db)

            print(f"Inserted {len(scraped_data)} items from {loc} into {source}")

        except Exception as e:
            print(f"Error processing {loc}: {e}")

def insert_scraped_data(source, data, db):
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
    if len(args) > 1 and args[1] == "None":
        args.pop(1)
    last_execution = sys.argv[1] if len(sys.argv) > 1 else None
    print(f"[DEBUG Container] ARGV: {sys.argv}")
    try:
        process_sitemap_entries(driver, db, last_execution)
    except Exception as e:
        logger.error(f"Erreur lors du traitement des entrées de sitemap : {e}")
    finally:
        logger.error(f"quit driver")
        driver.quit()
    logger.info("Application terminée.")