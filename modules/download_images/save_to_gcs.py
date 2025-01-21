
import requests
import time
import os
import logging
import logging.config
from psycopg2 import sql
from google.cloud import storage
from selenium.webdriver.common.by import By
from typing import Optional
from utils.db.postgres_utils import get_postgres_connection
from modules.scrappers.save_sitemaps_links_to_mongo import configure_selenium
from utils.config.settings import NB_DOWNLOAD_IMAGES


def download_and_upload_images_to_gcs(
    table_name: str,
    gcs_bucket_name: str,
    limit: Optional[int] = None
):
    """
    Lit depuis la table `table_name` de la base Postgres toutes les lignes dont
    la colonne `downloaded` est à false, télécharge l'image à partir de `image_url`,
    l'upload dans le bucket GCS `gcs_bucket_name`, puis met à jour la table :
      - `gcs_path` avec le chemin (blob name) de l'objet sur GCS
      - `downloaded` à true
    :param table_name: Nom de la table contenant les liens d'images
    :param gcs_bucket_name: Nom du bucket GCS où uploader les images
    :param limit: Optionnel, nombre maximal de lignes à traiter
    """
    # Connexion à la base de données
    conn = get_postgres_connection("dbdwhname")
    conn.autocommit = False  # On gère la transaction manuellement

    # Initialisation du client GCS
    storage_client = storage.Client()  # Assure-toi que les credentials sont bien configurés
    bucket = storage_client.bucket(gcs_bucket_name)

    try:
        with conn.cursor() as cur:
            # Préparation de la requête SELECT
            # On récupère uniquement les images non encore téléchargées (downloaded = false)
            query = sql.SQL("""
                SELECT image_id, cip_code, image_url
                FROM {table}
                WHERE downloaded = false
            """).format(table=sql.Identifier(table_name))

            if limit is not None:
                query = query + sql.SQL(" LIMIT {limit}").format(limit=sql.Literal(limit))

            cur.execute(query)
            rows = cur.fetchall()

            for row in rows:
                image_id, cip_code, image_url = row

                if not image_url:
                    continue  # On saute si l'URL est vide ou None

                # 1. Télécharger l'image
                try:
                    driver.get(image_url)
                    time.sleep(1)
                    image_element = driver.find_element(By.TAG_NAME, 'img')
                    file_extension = image_url.split('.')[-1] 
                
                except requests.RequestException as e:
                    # En cas d'erreur réseau, on peut gérer différemment
                    logging.info(f"Erreur lors du téléchargement de l'image {image_url} : {e}")
                    continue

                # 2. Définir le chemin (blob name) sur GCS
                #    Exemple de blob_name: "<id_dans_la_table>/<nom_de_fichier>"
                #    Vous pouvez choisir un format différent.
                blob_name = f"{cip_code}/{os.path.basename(image_url)}.{file_extension}"

                # 3. Uploader l'image dans GCS directement depuis la mémoire
                try:
                    blob = bucket.blob(blob_name)
                    # Méthode d'upload depuis un tableau d'octets
                    blob.upload_from_string(image_element.screenshot_as_png, content_type="image/jpeg")

                    # 4. Mettre à jour la table Postgres
                    update_query = sql.SQL("""
                        UPDATE {table}
                        SET gcs_path = %s, downloaded = true
                        WHERE image_id = %s
                    """).format(table=sql.Identifier(table_name))

                    cur.execute(update_query, (blob_name, image_id))
                    conn.commit()  # Commit pour valider cette mise à jour
                    logging.info(f"Image {image_url} => {blob_name} uploadée avec succès dans {gcs_bucket_name}.")
                except Exception as e:
                    conn.rollback()  # Annule la transaction si problème
                    logging.error(f"Erreur lors de l'upload ou de la mise à jour pour l'image {image_url} : {e}")

    except Exception as e:
        # Gestion d'erreurs globales
        conn.rollback()
        logging.error(f"Erreur inattendue : {e}")
    finally:
        driver.quit()
        conn.close()

if __name__ == "__main__":
    TABLE_NAME = "dim_images"
    GCS_BUCKET_NAME = "pharma_images"
    driver = configure_selenium()
    logging.config.fileConfig('utils/config/logging.conf')
    logger = logging.getLogger('download_images.save_to_gcs')

    download_and_upload_images_to_gcs(
        table_name=TABLE_NAME,
        gcs_bucket_name=GCS_BUCKET_NAME,
        limit=NB_DOWNLOAD_IMAGES
    )
