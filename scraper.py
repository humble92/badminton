from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os.path
import json
import re
from manage_csv import save_csv
from maps import Maps


LIST_URL = "https://www.toronto.ca/data/parks/prd/facilities/recreationcentres/index.html"
ITEM_URL_TEMPLATE = "https://www.toronto.ca{}"
JSON_FILE = "Recreation_Centres_Info.json"
CACHE_DIR = "data/cache"
PROGRAM = os.getenv('default_program')


class NotFoundProgramException(Exception):
    pass


class InvalidValueError(ValueError):
    pass


class BaseScraper:

    def __init__(self):
        # initiating the webdriver. Parameter includes the path of the webdriver.
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--headless") # Ensure GUI is off
        options.add_argument("--no-sandbox")

        dir_path = os.path.dirname(os.path.realpath(__file__))
        service = Service(f'{dir_path}/tool/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=options)


class ListScraper(BaseScraper):

    def __call__(self, url):

        self.driver.get(url)

        # this is just to ensure that the page is completely loaded
        time.sleep(5)
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        items = soup.tbody.find_all("tr")
        for i, item in enumerate(items):
            title, map_link = item.find_all("a")
            address = item.find("td", {"data-info": "Address"})

            yield {
                "id": i + 1,
                "title": title.get_text(strip=True),
                "address": address.get_text(strip=True),
                "url": title['href'],
                "map_link": map_link['href'],
            }

        self.driver.quit()  # closing the webdriver


class ItemScraper(BaseScraper):

    def __call__(self, url, program=PROGRAM):
        print(f'[Parsing] {url}')
        self.driver.get(url)

        # this is just to ensure that the page is completely loaded
        time.sleep(5)
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        try:
            rec_centre = soup.find("div", {"class":"accbox"}).find("h1")
            dropIns = soup.find("div", {"id":"pfrComplexTabs-dropin"})
            sports_tab = dropIns.find("tr", {"id":"dropin_Sports_0"})
            sports = sports_tab.tbody.find_all("tr")
            days = [ d.get_text(strip=True) for d in sports_tab.thead.find_all("th") ]
            days.pop(0)

            programs_count = 0
            for sport in sports:
                program_span = sport.find("span", {"class":"coursetitlecol"})
                
                if program_span.get_text() == program:
                    age = program_span.find_next_sibling("span").get_text(strip=True)
                    age = age[1:-1]
                    if not self._is_adult(age):
                        continue
                    
                    for i, timeslot_td in enumerate(sport.find_all("td")):
                        timeslot = timeslot_td.get_text(strip=True)
                        if timeslot:
                            programs_count += 1

                            yield {
                                "location": rec_centre.get_text(strip=True),
                                "day": days[i],
                                "timeslot": timeslot,
                                "age": age,
                                "url": url,
                            }

            if programs_count == 0:
                raise NotFoundProgramException(f"No Drop-in {program} programs found.")

        except NotFoundProgramException as e:
            print(f"{e} No relevant data exist. Exit gracefully.")
        except Exception as e:
            print(f"{e} Something wrong happens during parsing data. Exit gracefully.")

        self.driver.quit()  # closing the webdriver

    def _is_adult(self, age_string):
        age_string = age_string.replace("yrs", "")
        numbers = []

        for word in age_string.split():
            if word.isdigit():
                numbers.append(int(word))

        if len(numbers) >= 2 and numbers[-1] >= 18:
            return True
        elif len(numbers) == 1 and numbers[0] >= 18:
            # just in case
            if 'under' in age_string:
                return False
            else:
                return True

        return False


def scrape_list():
    it = ListScraper()(LIST_URL)
    rec_centres = {'rec_centres': []}
    while True:
        try:
            data = next(it)
            rec_centres['rec_centres'].append(data)
        except StopIteration:
            break

    write_json(rec_centres)
    print("List of Recreation Centres has been initialized.")


def scrape_item(url, program=PROGRAM):
    url = ITEM_URL_TEMPLATE.format(url)
    it = ItemScraper()(url, program)
    programs = []
    while True:
        try:
            data = next(it)
            programs.append(data)
        except StopIteration:
            break

    print(f"[Done] {url}")
    return programs


# function to add to JSON
def write_json(python_obj, filename=JSON_FILE, mode='w', indent=4):
    with open(filename, mode) as f:
        json.dump(python_obj, f, indent=indent)


def is_valid_postcode(postcode):
    result = re.findall(r'[a-z]{1}[0-9]{1}[a-z]{1}\s*[0-9]{1}[a-z]{1}[0-9]{1}', postcode)
    if len(result) == 1 and len(postcode) == 6:
        return True
    return False


def scrape_manager(postcode, program=PROGRAM, limit=5):

    if not is_valid_postcode(postcode):
        raise ValueError('Error: invalid postcode')

    postcode_cache_filename = f'{CACHE_DIR}/{postcode}.json'

    try:
        with open(postcode_cache_filename) as f:
            sorted_rec_centres = json.load(f)
    except FileNotFoundError:
        # only run when a postcode cache info doesn't exist
        if not os.path.exists(JSON_FILE):
            scrape_list()

        with open(JSON_FILE) as f:
            rec_centres = json.load(f)
            m = Maps()

            l = []
            for rec_centre in rec_centres['rec_centres']:
                dest = f"{rec_centre['address']} Toronto"
                distance = m.calc_distance(postcode, dest)
                l.append({
                    'id': rec_centre['id'],
                    'distance': distance,
                    'url': rec_centre['url'],
                })

                sorted_rec_centres = sorted(l, key=lambda d: d['distance'])

            write_json(sorted_rec_centres, postcode_cache_filename)

    programs_json = {program: []}
    for i, centre in enumerate(sorted_rec_centres):
        if limit:
            results = scrape_item(centre['url'], program)
            print(f'>>> {i+1} recreation centre(s) parsed.')
            limit -= 1

            if len(results):
                programs_json[program].extend(results)

    write_json(programs_json, f'data/output/{postcode}-{program}.json')
    save_csv(f'{postcode}-{program}', programs_json[program])
    return programs_json[program]
    
# simple tests
# scrape_list()
# scrape_item("/data/parks/prd/facilities/complex/13/index.html", "Volleyball")
# scrape_manager("M5T 1G4")
# scrape_manager("M5V 0R6", program="Volleyball", limit=5)

