import logging
import logging.config
from selenium.webdriver.common.by import By


def scrape_pharma_du_centre(driver, url):
    """
    Scrape les informations d'un produit sur le site Pharma GDD.

    Args:
        url (str): URL du produit à scraper.

    Returns:
        dict: Dictionnaire contenant les informations du produit ou None si une erreur survient.
    """
    try:
        driver.get(url)
        logging.info(f"Chargement de l'URL : {url}")
        driver.implicitly_wait(2)
        try:
            title = driver.find_element(By.CLASS_NAME, 'product-title').text
        except:
            title = None
        try:
            cip_code = driver.find_element(By.CLASS_NAME, 'product-ean13').text
        except:
            cip_code = None
        try:
            brand = driver.find_element(By.CLASS_NAME, 'product-brand').text
        except:
            brand = None
        try:
            price_element = driver.find_element(By.CSS_SELECTOR, 'span.price-sales')
            product_price = price_element.text
        except:
            product_price = None
        try:
            short_desc = driver.find_element(By.CSS_SELECTOR, 'div[itemprop="description"]').text
        except:
            short_desc = None
        try:
            breadcrumb = []
            ul_element = driver.find_element(By.CSS_SELECTOR, 'ul.breadcrumb')
            li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
            for li in li_elements:
                text = li.text.strip()
                if text:  
                    breadcrumb.append(text)
            categorie = breadcrumb[1]
            sous_categorie_1 = breadcrumb[2]
            sous_categorie_2 = breadcrumb[3]
            sous_categorie_3 = breadcrumb[4]
        except:
            categorie = None
            sous_categorie_1 = None
            sous_categorie_2 = None
            sous_categorie_3 = None
        try:
            image_element = driver.find_element(By.CSS_SELECTOR, '[itemprop="image"]')
            image_src = image_element.get_attribute("src")
        except:
            image_src = None
            print("Erreur lors de l'extraction de l'image:", e)
        try:
            div_infos = driver.find_element(By.CSS_SELECTOR, 'div.product-infos.mb-5')
            div_info =  div_infos.text.strip()
            long_desc = div_info
        except:
            div_info = None
            long_desc = None

        data = {}
        try:
            div_infos = driver.find_element(By.CSS_SELECTOR, 'div.product-infos.mb-5')
            lines = div_infos.text.split('\n')
            for line in lines:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().replace(' ', ' ')
                    val = parts[1].strip()
                    data[key] = val
        except:
            pass
         
        # Créer le dictionnaire du produit
        product_data = {
            "url_source": url,
            "title": title,
            "cip_code": cip_code,
            "brand": brand,
            "product_price": product_price,
            "short_desc": short_desc,
            "long_desc": long_desc,
            "categorie": categorie,
            "sous_categorie_1": sous_categorie_1,
            "sous_categorie_2": sous_categorie_2,
            "sous_categorie_3": sous_categorie_3,
            "image_src": image_src,
            "source": "pharmacie_du_centre"
        }
        product_data.update(data)
        return [product_data]

    except Exception as e:
        logging.error(f"Erreur lors du scraping pharmacie centre de {url} : {e}")
        return None