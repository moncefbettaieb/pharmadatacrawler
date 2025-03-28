import re
import logging
import logging.config
from utils.config import settings
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

def extract_clean_text_from_html(html: str) -> str:
    """Nettoie un bloc HTML et extrait le texte sans balises."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)

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
        driver.implicitly_wait(2)

        # Extraire le titre
        title = driver.find_element(By.CLASS_NAME, 'title').text
        if title is None or title == "Pharma GDD":
            return 
        try:
            reference = driver.find_element(By.CLASS_NAME, 'product-reference').text
            cip_code = "".join([char for char in reference if char.isdigit()])
        except:
            cip_code = None
        try:
            brand = driver.find_element(By.CSS_SELECTOR, 'a.brand').text
        except:
            brand = None
        try:
            long_desc = driver.find_element(By.CLASS_NAME, 'product-details').text
        except:
            long_desc = None
        try:
            short_desc = driver.find_element(By.CLASS_NAME, 'description').text
        except:
            short_desc = None
        try:
            breadcrumb_elements = driver.find_elements(By.CSS_SELECTOR, 'nav.nav-breadcrumb span[itemprop="name"]')
            breadcrumb_texts = [element.text for element in breadcrumb_elements]
            categorie = breadcrumb_texts[1]
            sous_categorie_1 = breadcrumb_texts[2]
            sous_categorie_2 = breadcrumb_texts[3]
        except:
            categorie = None
            sous_categorie_1 = None
            sous_categorie_2 = None
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, 'div.glider-container.main-image [data-src]')
            data_src_list = [element.get_attribute('data-src') for element in elements]
        except:
            print(f"le data_src_list n'est pas existant")

        try:
            presentation_html = driver.find_element(By.ID, "Présentation").get_attribute("outerHTML")
            presentation = extract_clean_text_from_html(presentation_html)
        except:
            presentation = None
        try:
            usage_html = driver.find_element(By.ID, "usages").get_attribute("outerHTML")
            usage = extract_clean_text_from_html(usage_html)
        except:
            usage = None
        try:
            composition_html = driver.find_element(By.ID, "Composition").get_attribute("outerHTML")
            composition = extract_clean_text_from_html(composition_html)
        except:
            composition = None
        try:
            texts = driver.find_elements(By.CLASS_NAME, 'text')
            match1 = re.search(r"(La composition.*?)(?=Posologie)", texts[1].text, re.DOTALL)
            match2 = re.search(r"(Posologie.*?)(?=Contre)", texts[1].text, re.DOTALL)
            match3 = re.search(r"(Contre.*?)(?=Conditionnement)", texts[1].text, re.DOTALL)
            match4 = re.search(r"(Conditionnement.*)", texts[1].text)
            if match1:
                composition_fp = match1.group(1).strip()
            else: 
                composition_fp = match1
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
            "url_source": url,
            "title": title,
            "cip_code": cip_code,
            "brand": brand,
            "short_desc": short_desc,
            "long_desc": long_desc,
            "presentation": presentation,
            "usage": usage,
            "composition": composition,
            "composition_fp": composition_fp,
            "posologie": posologie,
            "contre_indication": contre_indication,
            "conditionnement": conditionnement,
            "categorie": categorie,
            "sous_categorie_1": sous_categorie_1,
            "sous_categorie_2": sous_categorie_2,
            "image_links": data_src_list,
            "source": "pharma-gdd"
        }]
        return product_data

    except Exception as e:
        logging.error(f"Erreur lors du scraping Pharma GDD de {url} : {e}")
        return None
    
if __name__ == "__main__":
    driver = settings.configure_selenium()