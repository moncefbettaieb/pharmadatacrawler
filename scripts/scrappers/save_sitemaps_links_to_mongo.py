import re
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from config.settings import MONGO_CONFIG
from scripts.utils.MongoConnection import MongoConnection

def insert_sitemap(collection_name, document):
    db = MongoConnection.get_instance()
    db[collection_name].drop()
    collection = db[collection_name]
    collection.insert_one(document)

# Configuration de Selenium
def configure_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Exécuter en mode sans tête
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    service = Service(ChromeDriverManager().install(), log_path="chromedriver.log")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Fonction pour récupérer le contenu du fichier XML
def fetch_sitemap_with_selenium(url):
    driver = configure_selenium()
    try:
        print(f"Accessing {url}")
        driver.get(url)
        # Extraire le contenu de la page
        page_source = driver.page_source
        return page_source
    finally:
        driver.quit()

# Parser le fichier XML
def parse_sitemap(xml_content):
    """
    Parser le contenu XML d'un sitemap et extraire les balises <loc>, <lastmod>, et <priority>.
    """
    try:
        # Analysez le XML
        if not is_valid_sitemap(xml_content):
            print("Contenu non valide pour le parsing XML.")
            return []
        root = ET.fromstring(xml_content)
        namespace = {"ns": root.tag.split("}")[0].strip("{")}
        
        # Parcourir les balises <url>
        urls = []
        for url_element in root.findall("ns:url", namespace):
            loc = url_element.find("ns:loc", namespace)
            lastmod = url_element.find("ns:lastmod", namespace)
            priority = url_element.find("ns:priority", namespace)
            
            urls.append({
                "loc": loc.text if loc is not None else None,
                "lastmod": lastmod.text if lastmod is not None else None,
                "priority": float(priority.text) if priority is not None else None,
            })
        
        return urls

    except ET.ParseError as e:
        print(f"Erreur de parsing XML : {e}")
        return []

def is_valid_sitemap(content):
    soup = BeautifulSoup(content, "html.parser")
    if soup.find("html"):
        print("Le fichier semble être un contenu HTML, pas un XML valide.")
        return False
    return True

def load_sitemap_links(file_path):
    """
    Charger les liens des sitemaps depuis un fichier JSON.
    """
    with open(file_path, "r") as file:
        return json.load(file)
# Enregistrer dans MongoDB
def save_sitemaps_to_mongo_with_selenium(file_path, collection_name):
    sitemap_data = load_sitemap_links(file_path)
    for source, links in sitemap_data.items():
        for link in links:
            try:
                print(f"Processing sitemap from source '{source}': {link}")
                html_xml_content = fetch_sitemap_with_selenium(link)
                xml_content = extract_xml(html_xml_content)
                parsed_data = parse_sitemap(xml_content)
                for entry in parsed_data:
                    entry["source"] = source
                    entry["source_sitemap"] = link 
                    entry["inserted_day"] = INSERTED_DAY
                    insert_sitemap(collection_name, entry)
                print(f"Inserted {len(parsed_data)} entries from {link}")
            except Exception as e:
                print(f"Error processing {link}: {e}")

def extract_xml(content):
    """
    Extraire uniquement le contenu XML d'une réponse contenant du HTML et du XML.
    """
    # Rechercher un bloc XML commençant par <urlset> et se terminant par </urlset>
    match = re.search(r"<urlset.*?</urlset>", content, re.DOTALL)
    if match:
        return match.group(0)  # Retourne uniquement le contenu XML
    else:
        raise ValueError("Aucun contenu XML valide trouvé.")
    
if __name__ == "__main__":
    FILE_PATH = "resources/sitemap_links.json"  # Chemin du fichier contenant les liens
    COLLECTION_NAME = "sitemaps"
    INSERTED_DAY = datetime.now().strftime("%d%m%Y") 
    save_sitemaps_to_mongo_with_selenium(FILE_PATH, COLLECTION_NAME)
