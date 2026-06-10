# import os
# import time
# import re
# import csv
# import hashlib
# import requests
# from playwright.sync_api import sync_playwright

# # Configuration
# search_term_list = ["technology", "innovation", "AI", "robotics", "data science", "women", "diversity", "sustainability", "Men", "Culture", "foods"]
# SEARCH_QUERY = "Women"
# MAX_IMAGES = 50
# OUTPUT_DIR = "Iwaria_Press_Dataset"
# IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")

# # ─── Cookies de session Iwaria ─────────────────────────────────────────────────
# # 1. Connecte-toi manuellement sur https://iwaria.com/sign-in/ dans Chrome/Firefox
# # 2. Ouvre DevTools (F12) > Application > Cookies > https://iwaria.com
# # 3. Copie les cookies dont le nom commence par "wordpress_logged_in_" et "wordpress_"
# #    et colle leurs valeurs ci-dessous.
# IWARIA_COOKIES = [
#     # {"name": "wordpress_logged_in_xxxxxxxx", "value": "<valeur>", "domain": "iwaria.com", "path": "/"},
#     # {"name": "wordpress_sec_xxxxxxxx",        "value": "<valeur>", "domain": "iwaria.com", "path": "/"},
# ]
# # ───────────────────────────────────────────────────────────────────────────────

# os.makedirs(IMAGES_DIR, exist_ok=True)


# def clean_filename(text, img_id):
#     """Garde les 3 premiers mots-clés significatifs + l'ID pour garantir l'unicité."""
#     text = re.sub(r'[\\/*?:"<>|,]', "", text)
#     SKIP = {"africa", "photo", "free"}
#     keywords = [w.strip() for w in text.split() if len(w.strip()) > 2 and w.lower().strip() not in SKIP]
#     return f"{img_id}_" + "_".join(keywords[:3])


# def scrape_iwaria_IAC():
#     if not IWARIA_COOKIES:
#         print("ERREUR : IWARIA_COOKIES est vide. Lis les instructions en tête de fichier.")
#         return

#     metadata_list = []

#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=False,
#             args=["--host-resolver-rules=MAP iwaria.com 104.21.72.6"]
#         )
#         context = browser.new_context()

#         # Injection des cookies de session
#         context.add_cookies(IWARIA_COOKIES)
#         page = context.new_page()

#         # Vérifier que la session est active
#         page.goto("https://iwaria.com/", wait_until="domcontentloaded", timeout=60000)
#         time.sleep(2)
#         if "sign-in" in page.url or "login" in page.url:
#             print("ERREUR : cookies invalides ou expirés, reconnecte-toi et mets à jour IWARIA_COOKIES.")
#             browser.close()
#             return
#         print(f"Session active. URL : {page.url}")

#         # Navigation vers la page de recherche
#         url = f"https://iwaria.com/search/?q={SEARCH_QUERY}"
#         print(f"Navigation vers : {url}")
#         page.goto(url, wait_until="domcontentloaded", timeout=60000)
#         time.sleep(3)

#         image_count = 0
#         scroll_attempts = 0
#         max_scrolls = 15
#         visited_urls = set()
#         visited_hashes = set()

#         print("Collecte des images en cours (défilement de la page)...")
#         while image_count < MAX_IMAGES and scroll_attempts < max_scrolls:
#             img_elements = page.query_selector_all("img")

#             for img in img_elements:
#                 if image_count >= MAX_IMAGES:
#                     break

#                 src = img.get_attribute("data-src") or img.get_attribute("src")
#                 alt_text = img.get_attribute("alt")

#                 if not src or not alt_text or len(alt_text) < 10 or src in visited_urls:
#                     continue
#                 if src.endswith(".gif") or "iwaria.com/wp-content" in src:
#                     continue

#                 visited_urls.add(src)
#                 print(f"[tentative] Téléchargement : {alt_text[:40]}...")

#                 try:
#                     response = requests.get(src, timeout=10)
#                     if response.status_code == 200:
#                         content_hash = hashlib.md5(response.content).hexdigest()
#                         if content_hash in visited_hashes:
#                             print(f"  → doublon binaire ignoré : {src[-40:]}")
#                             continue
#                         visited_hashes.add(content_hash)

#                         image_count += 1
#                         img_id = f"IMG_{image_count:03d}"
#                         filename = f"{clean_filename(alt_text, img_id)}.jpg"
#                         filepath = os.path.join(IMAGES_DIR, filename)

#                         with open(filepath, "wb") as f:
#                             f.write(response.content)

#                         metadata_list.append({
#                             "ID_Image": img_id,
#                             "Nom_Fichier": filename,
#                             "Legende_Explicite": alt_text,
#                             "URL_Origine": src
#                         })
#                         print(f"  → [{img_id}] sauvegardé : {filename}")
#                     else:
#                         print(f"  → HTTP {response.status_code} pour {src[-40:]}")
#                 except Exception as e:
#                     print(f"  → Erreur téléchargement : {e}")

#             page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
#             time.sleep(2)
#             scroll_attempts += 1

#         browser.close()

#     csv_path = os.path.join(OUTPUT_DIR, "dataset_metadata_IACimages.csv")
#     with open(csv_path, mode="w", encoding="utf-8", newline="") as f:
#         writer = csv.DictWriter(f, fieldnames=["ID_Image", "Nom_Fichier", "Legende_Explicite", "URL_Origine"])
#         writer.writeheader()
#         writer.writerows(metadata_list)

#     print(f"\nScraping terminé ! {len(metadata_list)} images sauvegardées dans '{OUTPUT_DIR}'.")


# if __name__ == "__main__":
#     scrape_iwaria_IAC()


import os
import time
import re
import csv
import hashlib
import requests
from playwright.sync_api import sync_playwright

# Configuration
search_term_list = ["technology", "innovation", "AI", "robotics", "data science", "women", "diversity", "sustainability", "Men", "Culture", "foods"]
SEARCH_QUERY = "AI"
MAX_IMAGES = 50
OUTPUT_DIR = "Iwaria_Press_Dataset"
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")

# ─── Configuration du profil utilisateur ──────────────────────────────────────
# Remplacez "VotreNomUtilisateur" par votre nom de session Windows/Mac/Linux.
# Ce chemin permet à Playwright de charger vos sessions et cookies actifs.
USER_DATA_DIR = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default")
# Sur Mac, utilisez plutôt : os.path.expanduser("~/Library/Application Support/Google/Chrome/Default")
# Sur Linux, utilisez plutôt : os.path.expanduser("~/.config/google-chrome/Default")
# ───────────────────────────────────────────────────────────────────────────────

os.makedirs(IMAGES_DIR, exist_ok=True)


# torch>=2.0.0
# torchvision
# diffusers>=0.21.0
# transformers>=4.30.0
# accelerate>=0.21.0
# peft>=0.4.0
# datasets
# ftfy
# tensorboard
# scipy


def clean_filename(text, img_id):
    """Garde les 3 premiers mots-clés significatifs + l'ID pour garantir l'unicité."""
    text = re.sub(r'[\\/*?:"<>|,]', "", text)
    SKIP = {"africa", "photo", "free"}
    keywords = [w.strip() for w in text.split() if len(w.strip()) > 2 and w.lower().strip() not in SKIP]
    return f"{img_id}_" + "_".join(keywords[:3])


def scrape_iwaria_IAC():
    metadata_list = []

    with sync_playwright() as p:
        print("Lancement du navigateur avec votre profil persistant...")
        
        # Initialisation du contexte persistant à la place d'un contexte vierge
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,  # Recommandé False pour utiliser le profil utilisateur existant
            args=["--host-resolver-rules=MAP iwaria.com 104.21.72.6"]
        )
        
        page = context.new_page()

        # Vérifier si la session partagée est active
        print("Vérification de l'état de la connexion sur Iwaria...")
        page.goto("https://iwaria.com/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)
        
        if "sign-in" in page.url or "login" in page.url:
            print("ERREUR : Vous n'êtes pas connecté sur ce profil de navigateur.")
            print("Veuillez ouvrir Chrome, vous connecter manuellement sur https://iwaria.com/, puis relancer ce script.")
            context.close()
            return
            
        print(f"Session active vérifiée. URL actuelle : {page.url}")

        # Navigation vers la page de recherche
        url = f"https://iwaria.com/search/?q={SEARCH_QUERY}"
        print(f"Navigation vers le catalogue de recherche : {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        image_count = 0
        scroll_attempts = 0
        max_scrolls = 15
        visited_urls = set()
        visited_hashes = set()

        print("Collecte des images en cours (défilement de la page)...")
        while image_count < MAX_IMAGES and scroll_attempts < max_scrolls:
            img_elements = page.query_selector_all("img")

            for img in img_elements:
                if image_count >= MAX_IMAGES:
                    break

                src = img.get_attribute("data-src") or img.get_attribute("src")
                alt_text = img.get_attribute("alt")

                if not src or not alt_text or len(alt_text) < 10 or src in visited_urls:
                    continue
                if src.endswith(".gif") or "iwaria.com/wp-content" in src:
                    continue

                visited_urls.add(src)
                print(f"[tentative] Téléchargement : {alt_text[:40]}...")

                try:
                    # Utilisation des cookies du contexte de navigation pour la requête de téléchargement
                    # afin de s'assurer d'obtenir la version HD autorisée par votre compte
                    session_cookies = {c['name']: c['value'] for c in context.cookies()}
                    response = requests.get(src, cookies=session_cookies, timeout=10)
                    
                    if response.status_code == 200:
                        content_hash = hashlib.md5(response.content).hexdigest()
                        if content_hash in visited_hashes:
                            print(f"  → doublon binaire ignoré : {src[-40:]}")
                            continue
                        visited_hashes.add(content_hash)

                        image_count += 1
                        img_id = f"IMG_{image_count:03d}"
                        filename = f"{clean_filename(alt_text, img_id)}.jpg"
                        filepath = os.path.join(IMAGES_DIR, filename)

                        with open(filepath, "wb") as f:
                            f.write(response.content)

                        metadata_list.append({
                            "ID_Image": img_id,
                            "Nom_Fichier": filename,
                            "Legende_Explicite": alt_text,
                            "URL_Origine": src
                        })
                        print(f"  → [{img_id}] sauvegardé : {filename}")
                    else:
                        print(f"  → HTTP {response.status_code} pour {src[-40:]}")
                except Exception as e:
                    print(f"  → Erreur téléchargement : {e}")

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            scroll_attempts += 1

        context.close()

    csv_path = os.path.join(OUTPUT_DIR, "dataset_metadata_IACimages.csv")
    with open(csv_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ID_Image", "Nom_Fichier", "Legende_Explicite", "URL_Origine"])
        writer.writeheader()
        writer.writerows(metadata_list)

    print(f"\nScraping terminé ! {len(metadata_list)} images sauvegardées dans '{OUTPUT_DIR}'.")


if __name__ == "__main__":
    scrape_iwaria_IAC()