import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from utils.db import db_utils


service = Service('/Users/mbettaieb/Downloads/chromedriver-mac-arm64/chromedriver')
driver = webdriver.Chrome(service=service)
url = "https://www.google.com/search?q="

def run_scraper():
    service = Service('/Users/mbettaieb/Downloads/chromedriver-mac-arm64/chromedriver')
    driver = webdriver.Chrome(service=service)
    time.sleep(1)
    isbns = db_utils.read_isbn(limit=10)
    try:
        for (isbn,) in isbns:
            print(isbn)
            scrapper_urls_for_isbn(isbn)
    except Exception as e:
        print(f"fin d'extraction après : {e}")
    finally:
        driver.quit()

def scrapper_urls_for_isbn(isbn):
    url_isbn = url + str(isbn)
    driver.get(url_isbn)
    time.sleep(1)
    print(driver)
