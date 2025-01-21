import sys
import logging
import logging.config
from utils.config import settings
from modules.scrappers.save_sitemaps_links_to_mongo import runSitemapLinks
from modules.scrappers.save_sitemaps_links_to_mongo import configure_selenium
from modules.scrappers.pharma_gdd_scraper import runRunPharmaDataScrapping

def main():
    logging.config.fileConfig('utils/config/logging.conf')
    logger = logging.getLogger('scrapper')
    logger.info("Application Started.")
    logger.info(f"Environnement : {settings.APP_ENV}")
    driver = configure_selenium()
    runSitemapLinks(driver)
    runRunPharmaDataScrapping(driver)
    logger.info("Application terminée.")

if __name__ == "__main__":
    sys.exit(main())