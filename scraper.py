from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os.path
import json


LIST_URL = "https://www.toronto.ca/data/parks/prd/facilities/recreationcentres/index.html"
ITEM_URL = "https://www.toronto.ca/data/parks/prd/facilities/complex/3643/index.html"
JSON_FILE = "Recreation_Centres_Info.json"


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
        for item in items:
            title, map_link = item.find_all("a")
            address = item.find("td", {"data-info": "Address"})

            yield {
                "title": title.get_text(strip=True),
                "address": address.get_text(strip=True),
                "map_link": map_link['href'],
            }

        self.driver.quit()  # closing the webdriver


class ItemScraper(BaseScraper):

    def __call__(self, url, program="Badminton"):

        self.driver.get(url)

        # this is just to ensure that the page is completely loaded
        time.sleep(5)
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        try:
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
                            print(i)
                            programs_count += 1

                            yield {
                                "title": program,
                                "age": age,
                                "day": days[i],
                                "timeslot": timeslot,
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


class NotFoundProgramException(Exception):
    pass

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


def scrape_item(program="Badminton"):
    it = ItemScraper()(ITEM_URL, program)
    programs = {program: []}
    while True:
        try:
            data = next(it)
            programs[program].append(data)
        except StopIteration:
            break

    write_json(programs, f'programs_data/{program}.json')
    print("Drop-in badminton programs have been parsed.")


# function to add to JSON
def write_json(python_obj, filename=JSON_FILE, mode='w', indent=4):
    with open(filename, mode) as f:
        json.dump(python_obj, f, indent=indent)


# temporarily test w/ Volleyball
scrape_item("Volleyball")

