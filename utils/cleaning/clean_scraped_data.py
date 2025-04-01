import json
import re
from typing import Optional, Union

def clean_scraped_data(product_data: dict) -> dict:
    """
    Prend un dictionnaire avec les clés suivantes (exemple):
      {
        "url_source": "...",
        "title": "...",
        "cip_code": "...",
        "brand": "...",
        "short_desc": "...",
        "long_desc": "...",
        "composition": "...",
        "posologie": "...",
        "contre_indication": "...",
        "conditionnement": "...",
        "categorie": "...",
        "sous_categorie_1": "...",
        "sous_categorie_2": "...",
        "image_links": [... list de strings ...]
      }
    et retourne un dictionnaire nettoyé selon différentes règles :
      - Remplacer "null" (string) par None (type None).
      - Supprimer les espaces en trop (strip).
      - Parser une éventuelle structure JSON dans un champ s'il y en a (exemple).
      - Gérer des champs manquants / vides.
      - Nettoyer d'éventuels caractères indésirables (ex: \n, \t, etc.).
    """

    # Copie pour ne pas modifier l'original
    cleaned_data = product_data.copy()

    # Exemples de fonctions de nettoyage
    def _nullify_string(s: str) -> Optional[str]:
        """
        Si la chaîne de caractères est "null", on la transforme en None.
        Sinon, on renvoie la chaîne stripée.
        """
        if s.strip().lower() == "null":
            return None
        # On retourne la chaîne sans espaces inutiles
        stripped = s.strip()
        # Si la chaîne est vide après strip(), on peut la considérer comme None
        return stripped if stripped else None

    def _parse_json(s: str) -> Union[dict, str]:
        """
        Si la chaîne semble être du JSON, on la parse et on renvoie le dict.
        Sinon, on renvoie la chaîne telle quelle.
        On peut adapter la détection de JSON selon les cas.
        """
        # On strip d'abord la chaîne
        s = s.strip()
        # Petit test grossier pour repérer un objet JSON
        # (peut être adapté ou rendu plus robuste).
        if (s.startswith('{') and s.endswith('}')) or (s.startswith('[') and s.endswith(']')):
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                pass
        return s

    def _remove_wrapping_quotes(s: str) -> str:
        """
        Si la chaîne commence et se termine par un guillemet ("),
        on retire le premier et le dernier caractère.

        Exemple :
          "Bébé et Maman" -> Bébé et Maman
          "Hello" -> Hello
          TOTO -> TOTO (inchangé, car pas de guillemets)
        """
        s = s.strip()
        if len(s) > 1 and s.startswith('"') and s.endswith('"'):
            return s[1:-1].strip()
        return s
    
    def _clean_text_field(val: str) -> Union[str, None, dict]:
        """
        Nettoie une valeur textuelle :
          - transforme "null" en None
          - strip() pour enlever espaces début/fin
          - parse JSON si nécessaire
          - enlève caractères parasites (ex: \r, \n...) si besoin
        """
        if not isinstance(val, str):
            return val  # si pas string, on ne modifie pas
        # 1) Check si "null"
        maybe_null = _nullify_string(val)
        if maybe_null is None:
            return None
        # 2) Enlever d'éventuels guillemets externes
        no_quotes = _remove_wrapping_quotes(maybe_null)
        # 3) Tenter un parse JSON
        maybe_parsed = _parse_json(no_quotes)
        # 4) Nettoyage additionnel : enlever les retours à la ligne multiples
        if isinstance(maybe_parsed, str):
            # Suppression des \r \n multiples (ou on peut les remplacer par un espace)
            cleaned = re.sub(r'[\r\n\t]+', ' ', maybe_parsed)
            # On retire aussi les espaces multiples
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            return cleaned if cleaned else None
        else:
            # Le champ était du JSON parseable et on a un dict/list
            return maybe_parsed
    
    # Exemple : on applique _clean_text_field à certains champs spécifiques
    text_fields = [
        "title", "cip_code", "brand", "short_desc", "long_desc",
        "composition", "posologie", "contre_indication", "conditionnement",
        "categorie", "sous_categorie_1", "sous_categorie_2"
    ]
    for field in text_fields:
        if field in cleaned_data and cleaned_data[field] is not None:
            cleaned_data[field] = _clean_text_field(cleaned_data[field])

    # Gérer la liste d'images (ex: supprimer doublons, enlever None, etc.)
    if "image_links" in cleaned_data and isinstance(cleaned_data["image_links"], list):
        # Nettoyage élémentaire : strip de chaque URL, enlever celles qui valent "null"
        cleaned_images = []
        for link in cleaned_data["image_links"]:
            if isinstance(link, str):
                link_cleaned = _clean_text_field(link)
                if link_cleaned is not None:
                    cleaned_images.append(link_cleaned)
        cleaned_data["image_links"] = list(dict.fromkeys(cleaned_images))  # Supprimer doublons

    # On peut aussi normaliser/valider le cip_code
    # Par exemple, s'assurer qu'il n'y ait que des chiffres :
    if cleaned_data.get("cip_code"):
        # Ne garder que les digits
        only_digits = re.sub(r'\D', '', cleaned_data["cip_code"])
        cleaned_data["cip_code"] = only_digits if only_digits else None

    
    return [cleaned_data]
