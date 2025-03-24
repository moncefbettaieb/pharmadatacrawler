import time
import logging
import logging.config
from typing import Optional, Dict, List
from collections import defaultdict

from selenium.webdriver.common.by import By
from psycopg2 import sql
from google.cloud import storage

from utils.config import settings
from utils.db.postgres_utils import get_postgres_connection


def download_and_upload_images_to_gcs(
    table_name: str,
    gcs_bucket_name: str,
    limit: Optional[int] = None
):
    """
    1) Récupère, depuis la table `table_name`, toutes les images non encore téléchargées (downloaded = false).
    2) Regroupe ces images par cip_code.
    3) Pour chaque cip_code, télécharge successivement les images, les nomme code_cip_1.jpeg, code_cip_2.jpeg, etc.
    4) Les envoie dans le bucket GCS `gcs_bucket_name`.
    5) Met à jour la table : gcs_path = le nouveau chemin, et downloaded = true.
    """

    # Connexion à la base de données
    conn = get_postgres_connection("dbdwhname")
    conn.autocommit = False  # On gère la transaction manuellement

    # Initialisation du client GCS
    storage_client = storage.Client()  # Assure-toi que GOOGLE_APPLICATION_CREDENTIALS est bien configurée
    bucket = storage_client.bucket(gcs_bucket_name)

    try:
        with conn.cursor() as cur:
            # Préparation de la requête SELECT
            query = sql.SQL("""
                SELECT image_id, cip_code, image_url
                FROM {table}
                WHERE downloaded = false
            """).format(table=sql.Identifier(settings.APP_ENV, table_name))
            print("query1 : ", query)
            if limit is not None:
                query = query + sql.SQL(" LIMIT {limit}").format(limit=sql.Literal(limit))
            cur.execute(query)
            rows = cur.fetchall()

            # Regrouper les images par cip_code
            images_by_cip: Dict[str, List] = defaultdict(list)
            for (image_id, cip_code, image_url) in rows:
                if cip_code and image_url:
                    images_by_cip[cip_code].append((image_id, image_url))

            # Pour chaque CIP, on boucle sur les images de ce CIP
            for cip_code, image_data_list in images_by_cip.items():
                total_images = len(image_data_list)
                logging.info(f"Traitement de {total_images} image(s) pour le CIP {cip_code}.")
                for reverse_idx, (image_id, image_url) in zip(reversed(range(total_images)), image_data_list):
                    try:
                        # 1) Charger la page dans Selenium
                        driver.get(image_url)
                        time.sleep(1)

                        # 2) Récupérer la balise <img> et faire un screenshot
                        image_element = driver.find_element(By.TAG_NAME, 'img')
                        image_content = image_element.screenshot_as_png
                    except Exception as e:
                        # Erreur réseau ou Selenium
                        logging.warning(f"Erreur lors du téléchargement de l'image {image_url} : {e}")
                        continue

                    # 3) Définir le chemin (blob_name) et nom de fichier
                    #    Exemple : CIP123456_1.jpeg
                    #    On peut aussi les ranger dans un dossier CIP, ex: {cip_code}/{cip_code}_{reverse_idx}.jpeg
                    filename = f"{cip_code}_{reverse_idx}.jpeg"
                    blob_name = f"{cip_code}/{filename}"  # sous-dossier = cip_code

                    # 4) Uploader dans GCS
                    try:
                        blob = bucket.blob(blob_name)
                        blob.upload_from_string(image_content, content_type="image/jpeg")

                        # 5) Mettre à jour la BDD
                        update_query = sql.SQL("""
                            UPDATE {table}
                            SET gcs_path = %s, downloaded = true
                            WHERE image_id = %s
                        """).format(table=sql.Identifier(settings.APP_ENV, table_name))
                        cur.execute(update_query, (blob_name, image_id))
                        conn.commit()
                        logging.info(f"Image {image_url} => {blob_name} uploadée avec succès.")
                    except Exception as e:
                        conn.rollback()
                        logging.error(f"Erreur lors de l'upload ou de la mise à jour pour l'image {image_url} : {e}")

    except Exception as e:
        # Gestion d'erreurs globales
        conn.rollback()
        logging.error(f"Erreur inattendue : {e}")
    finally:
        driver.quit()
        conn.close()


if __name__ == "__main__":
    logging.config.fileConfig('utils/config/logging.conf')
    logger = logging.getLogger('save_to_gcs')
    logger.info("Début du script de téléchargement et upload d'images.")

    driver = settings.configure_selenium()
    table_name = settings.SAVE_GCS_IMAGES_CONFIG[f"table_name"]
    gcs_bucket_name = settings.SAVE_GCS_IMAGES_CONFIG["gcs_bucket_name"]
    limit = settings.SAVE_GCS_IMAGES_CONFIG["nb_download_images"]

    download_and_upload_images_to_gcs(
        table_name=table_name,
        gcs_bucket_name=gcs_bucket_name,
        limit=limit  # ou None si vous voulez traiter toutes les images
    )

    logger.info("Fin du script.")
