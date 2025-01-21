import sys
import re
import logging
import logging.config
from datetime import datetime
from selenium.webdriver.common.by import By
from utils.db.MongoConnection import MongoConnection
from modules.scrappers.pharmacie_du_centre_scrapper import scrape_pharma_du_centre

def insert_scraped_data(source, data, db, last_execution=None):
    """
    Insérer les données dans la collection MongoDB avec des champs supplémentaires.
    """
    collection = db[source]
    for item in data:
        item["first_insertion"] = datetime.now() if last_execution is None else None
        item["last_update"] = datetime.now() if last_execution is not None else None
        collection.insert_one(item)

def process_sitemap_entries(driver, db, last_execution=None,):
    """
    Traiter les entrées de la collection `sitemaps` en fonction de last_execution.
    """
    sitemaps_collection = db["sitemaps"]

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
                    scraped_data = scrape_pharma_gdd(driver, loc)
                case "pharmacie-du-centre":
                    scraped_data = scrape_pharma_du_centre(driver, loc)
            for item in scraped_data:
                item["source"] = source
                insert_scraped_data(source, scraped_data, db, last_execution)

            print(f"Inserted {len(scraped_data)} items from {loc} into {source}")

        except Exception as e:
            print(f"Error processing {loc}: {e}")

def scrape_pharma_gdd(driver, url):
    """
    Scrape les informations d'un produit sur le site Pharma GDD.

    Args:
        driver (webdriver.Chrome): Instance du navigateur Selenium.
        url (str): URL du produit à scraper.

    Returns:
        dict: Dictionnaire contenant les informations du produit ou None si une erreur survient.
    """
    try:
        # Charger la page du produit
        driver.get(url)
        logging.info(f"Chargement de l'URL : {url}")
        
        # Attendre que la page se charge
        driver.implicitly_wait(3)

        # Extraire le titre
        title = driver.find_element(By.CLASS_NAME, 'title').text
        if title is None or title == "Pharma GDD":
            return 
        try:
            reference = driver.find_element(By.CLASS_NAME, 'product-reference').text
            cip_code = "".join([char for char in reference if char.isdigit()])
        except:
            cip_code = ""
        try:
            brand = driver.find_element(By.CSS_SELECTOR, 'a.brand').text
        except:
            brand = ""
        try:
            long_desc = driver.find_element(By.CLASS_NAME, 'product-details').text
        except:
            long_desc = ""
        try:
            short_desc = driver.find_element(By.CLASS_NAME, 'description').text
        except:
            short_desc = ""
        try:
            breadcrumb_elements = driver.find_elements(By.CSS_SELECTOR, 'nav.nav-breadcrumb span[itemprop="name"]')
            breadcrumb_texts = [element.text for element in breadcrumb_elements]
            categorie = breadcrumb_texts[1]
            sous_categorie_1 = breadcrumb_texts[2]
            sous_categorie_2 = breadcrumb_texts[3]
        except:
            categorie = ""
            sous_categorie_1 = ""
            sous_categorie_2 = ""
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, 'div.glider-container.main-image [data-src]')
            data_src_list = [element.get_attribute('data-src') for element in elements]
        except:
            print(f"le data_src_list n'est pas existant")

        try:
            texts = driver.find_elements(By.CLASS_NAME, 'text')
            match1 = re.search(r"(La composition.*?)(?=Posologie)", texts[1].text, re.DOTALL)
            match2 = re.search(r"(Posologie.*?)(?=Contre)", texts[1].text, re.DOTALL)
            match3 = re.search(r"(Contre.*?)(?=Conditionnement)", texts[1].text, re.DOTALL)
            match4 = re.search(r"(Conditionnement.*)", texts[1].text)
            if match1:
                composition = match1.group(1).strip()
            else: 
                composition = match1
            if match2:
                posologie = match2.group(1).strip()
            else: 
                posologie = match2
            if match3:
                contre_indication = match3.group(1).strip()
            else: 
                contre_indication = match3
            if match4:
                conditionnement = match4.group(1).strip()
            else: 
                conditionnement = match4
        except:
            print(f"le texts n'est pas existant")

        # Créer le dictionnaire du produit
        product_data = [{
            "title": title,
            "cip_code": cip_code,
            "brand": brand,
            "short_desc": short_desc,
            "long_desc": long_desc,
            "composition": composition,
            "posologie": posologie,
            "contre_indication": contre_indication,
            "conditionnement": conditionnement,
            "categorie": categorie,
            "sous_categorie_1": sous_categorie_1,
            "sous_categorie_2": sous_categorie_2,
            "image_links": data_src_list
        }]

        return product_data

    except Exception as e:
        logging.error(f"Erreur lors du scraping Pharma GDD de {url} : {e}")
        return None

def main(driver):
    logger = logging.getLogger('scrapper')
    logger.info(f"Pharma Scrapper")
    db = MongoConnection.get_instance()
    last_execution_arg = sys.argv[1] if len(sys.argv) > 1 else None
    last_execution = (
        datetime.strptime(last_execution_arg, "%Y-%m-%d") if last_execution_arg else None
    )    
    try:
        process_sitemap_entries(driver, db, last_execution)
    except Exception as e:
        logger.error(f"Erreur lors du traitement des entrées de sitemap : {e}")
    finally:
        driver.quit()
def runRunPharmaDataScrapping(driver):
    main(driver)