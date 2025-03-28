import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from utils.config import settings
from utils.db.MongoConnection import MongoConnection

def insert_sitemap(db, collection_name, document):
    collection = db[collection_name]
    filter_query = {
        "loc": document["loc"],
        "source": document["source"]
    }
    update_doc = {
        "$set": {
            "lastmod": document["lastmod"],
            "priority": document["priority"],
            "source_sitemap": document["source_sitemap"],
            "inserted_day": document["inserted_day"],
        }
    }

    collection.update_one(filter_query, update_doc, upsert=True)

def fetch_sitemap_with_selenium(driver, url):
    try:
        print(f"Accessing {url}")
        driver.get(url)
        # Extraire le contenu de la page
        page_source = driver.page_source
        return page_source
    except Exception as e:
                print(f"Error processing {url}: {e}")

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

            lastmod_dt = None
            if lastmod is not None:
                try:
                    lastmod_dt = datetime.fromisoformat(lastmod.text)
                except ValueError:
                    try:
                        lastmod_dt = datetime.strptime(lastmod.text, "%Y-%m-%d")
                    except ValueError:
                        print(f"Format de date inconnu pour lastmod: {lastmod.text}")
            
            urls.append({
                "loc": loc.text if loc is not None else None,
                "lastmod": lastmod_dt,
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

def save_sitemaps_to_mongo_with_selenium(driver, db, file_path, collection_name, INSERTED_DAY):
    sitemap_data = load_sitemap_links(file_path)
    for source, links in sitemap_data.items():
        for link in links:
            try:
                print(f"Processing sitemap from source '{source}': {link}")
                html_xml_content = fetch_sitemap_with_selenium(driver, link)
                xml_content = extract_xml(html_xml_content)
                parsed_data = parse_sitemap(xml_content)
                for entry in parsed_data:
                    entry["source"] = source
                    entry["source_sitemap"] = link 
                    entry["inserted_day"] = INSERTED_DAY
                    entry["processed_mod"] = None
                    insert_sitemap(db, collection_name, entry)
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
    FILE_PATH = "resources/sitemap_links.json"
    COLLECTION_NAME = "sitemaps"
    INSERTED_DAY = datetime.now().strftime("%d%m%Y")
    db = MongoConnection.get_instance()
    driver = settings.configure_selenium()
    save_sitemaps_to_mongo_with_selenium(driver, db, FILE_PATH, COLLECTION_NAME, INSERTED_DAY)