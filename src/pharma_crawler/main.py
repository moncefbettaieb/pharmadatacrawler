import logging
import logging.config
from datetime import datetime
from utils.config import settings
from utils.db.MongoConnection import MongoConnection
from modules.scrappers.save_sitemaps_links_to_mongo import save_sitemaps_to_mongo_with_selenium

if __name__ == "__main__":
    logging.config.fileConfig('utils/config/logging.conf')
    logger = logging.getLogger('scrapper')
    logger.info("Application Started.")
    logger.info(f"Environnement : {settings.APP_ENV}")
    driver = settings.configure_selenium()
    FILE_PATH = "resources/sitemap_links.json"
    COLLECTION_NAME = "sitemaps"
    INSERTED_DAY = datetime.now().strftime("%d%m%Y")
    db = MongoConnection.get_instance()
    save_sitemaps_to_mongo_with_selenium(driver, db, FILE_PATH, COLLECTION_NAME, INSERTED_DAY)
    #pharma_scrapper(driver)
    #save_to_gcs(driver)
    logger.info("Application terminée.")