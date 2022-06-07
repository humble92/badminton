import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os.path
import json


URL = "https://www.toronto.ca/data/parks/prd/facilities/recreationcentres/index.html"
JSON_FILE = "Recreation_Centres_Info.json"

class BaseScraping:

    def __call__(self, url):
        # initiating the webdriver. Parameter includes the path of the webdriver.
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--headless") # Ensure GUI is off
        options.add_argument("--no-sandbox")

        dir_path = os.path.dirname(os.path.realpath(__file__))
        service = Service(f'{dir_path}/tool/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)

        # this is just to ensure that the page is completely loaded
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        items = soup.tbody.find_all("tr")
        for item in items:
            title, map_link = item.find_all("a")
            address = item.find("td", {"data-info": "Address"})

            yield {
                "title": title.get_text(strip=True),
                "address": address.get_text(strip=True),
                "map_link": map_link['href'],
            }

        driver.quit()  # closing the webdriver


def scrape():
    it = BaseScraping()(URL)
    rec_centres = {'rec_centres': []}
    while True:
        try:
            data = next(it)
            rec_centres['rec_centres'].append(data)
        except StopIteration:
            break

    write_json(rec_centres)
    print(f"Completed")


# function to add to JSON
def write_json(python_obj, filename=JSON_FILE, mode='w', indent=4):
    with open(filename, mode) as f:
        json.dump(python_obj, f, indent=indent)


scrape()

