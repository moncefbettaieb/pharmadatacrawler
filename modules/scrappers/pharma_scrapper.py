import sys
import logging
import logging.config
from datetime import datetime
from utils.config import settings
from utils.db.MongoConnection import MongoConnection
from modules.scrappers import pharma_gdd_scraper
from modules.scrappers import pharmacie_du_centre_scrapper

def process_sitemap_entries(driver, db, last_execution=None, sources=None):
    """
    Traiter les entrées de la collection `sitemaps` en fonction de last_execution et d'une liste de sources.
    """
    sitemaps_collection = db["sitemaps"]
    
    # Si le driver ou la connexion à la DB ne sont pas fournis, on les configure.
    if driver is None:
        driver = settings.configure_selenium()
    if db is None:
        db = MongoConnection.get_instance()
    
    logger.info(f"Last execution was at : {last_execution}.")
    
    # Construire la requête en fonction de last_execution et des sources
    query = {
    "$or": [
        { "processed_mod": { "$exists": False } },
        { "processed_mod": None },
        {
            "$expr": {
                "$gt": ["$lastmod", "$processed_mod"]
            }
        }
    ]
}
    if last_execution is not None and last_execution != "None":
        last_execution_dt = datetime.strptime(last_execution, "%d-%m-%Y")
        query["lastmod"] = {"$gt": last_execution_dt.strftime("%Y-%m-%d")}
    
    if sources:
        # Filtrer par la liste de sources (ex.: ["pharma-gdd", "pharmacie-du-centre"])
        query["source"] = {"$in": sources}
    
    # Récupération des documents à traiter
    items = sitemaps_collection.find(query)
    doc_count = sitemaps_collection.count_documents(query)
    if last_execution and last_execution != "None":
        print(f"Processing {doc_count} items since {last_execution}")
    else:
        print(f"Processing {doc_count} items with no last_execution filter")
    
    # Traitement de chaque document
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
                case _:
                    print(f"No scrapper implemented for source: {source}")
                    continue

            for item in scraped_data:
                if item is not None: 
                    item["source"] = source
            insert_scraped_data(source.replace('-', '_'), scraped_data, db)
            sitemaps_collection.update_one(
            {"_id": sitemap_entry["_id"]},
            {"$set": {"processed_mod": sitemap_entry["lastmod"]}})
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
    logger = logging.getLogger("pharma_crawler")
    logger.info(f"Application Started Environnement : {settings.APP_ENV}.")
    
    db = MongoConnection.get_instance()
    driver = settings.configure_selenium()
    
    # Récupération des arguments
    # sys.argv[1] = last_execution  (optionnel)
    # sys.argv[2] = liste de sources séparées par des virgules (optionnel)
    last_execution = sys.argv[1] if len(sys.argv) > 1 and (sys.argv[1] != "None" or sys.argv[1] is not None) else None
    
    # On parse le second argument s'il est présent et on split par virgule
    if len(sys.argv) > 2:
        sources = sys.argv[2].split(',')
        # Nettoyage éventuel, ex.: supprimer d'éventuels espaces
        sources = [s.strip() for s in sources if s.strip()]
    else:
        sources = None
    
    print(f"[DEBUG Container] ARGV: {sys.argv}")
    print(f"[DEBUG] last_execution={last_execution}, sources={sources}")
    
    try:
        process_sitemap_entries(driver, db, last_execution, sources)
    except Exception as e:
        logger.error(f"Erreur lors du traitement des entrées de sitemap : {e}")
    finally:
        logger.info("quit driver")
        driver.quit()
    
    logger.info("Application terminée.")
