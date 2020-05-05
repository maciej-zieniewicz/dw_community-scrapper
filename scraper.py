import time

import requests
import numpy as np
from bs4 import BeautifulSoup
from slugify import slugify

import json


class PageScrapper:

    def __init__(self, url):

        self.url = url
        self.last_page = self.get_last_page_number()
        self.data_dict = {}

        print(f"Total number of pages: {self.last_page}")

    def get_last_page_number(self):
        page = self.read_page_content(self.url)
        last_page_element = page.find("a", {"data-cy": "page-link-last"}).find('span').get_text()
        return last_page_element

    def find_advertisements(self):

        iterator = 0
        for page_number in range(int(self.last_page) + 1):

            print(f"Page {page_number + 1}/{self.last_page} processing...")
            if page_number == 0:
                page = self.read_page_content(self.url)
            else:
                page = self.read_page_content(self.url + f'&page={page_number}')
            advertisements = page.findAll("a", {"data-cy": "listing-ad-title"})

            for idx, advert in enumerate(advertisements):
                if 'otodom.pl' in advert['href']:
                    pass
                else:
                    data = self.parse_advertisement(advert['href'])
                    self.data_dict[iterator] = data
                    print(data)
                    iterator += 1
                time.sleep(1)

        return 1

    def parse_advertisement(self, url):

        data = {}

        page = self.read_page_content(url)

        container = page.find('div', {'class': 'offerbody'})
        title_container = container.find('div', 'offer-titlebox')
        desc_container = container.find('div', {'class': 'descriptioncontent'})

        data['nazwa'] = title_container.find('h1').get_text().strip()

        try:
            data['cena'] = float(container.find('div', {'class': 'price-label'}).find('strong')
                                 .get_text().replace('zł', '').replace(' ', ''))
        except ValueError:
            data['cena'] = np.nan

        data['lokalizacja'] = title_container.select('a.show-map-link')[0].get_text()

        parameters = desc_container.find_all('table', {'class': 'item'})

        for param in parameters:
            param_name = param.find('th').get_text()
            param_value = param.find('td', {'class': 'value'}).get_text().strip().replace("\t", "").replace("\n", "")
            data[slugify(param_name)] = param_value

        data['tresc'] = desc_container.find('div', {'id': 'textContent'}).get_text().strip()

        return data

    def read_page_content(self, url):
        page = requests.get(url)
        return BeautifulSoup(page.content, "html.parser")

    def create_json(self):
        with open('data.json', 'w') as fp:
            json.dump(self.data_dict, fp)


newURL = ""

scraper = PageScrapper(newURL)
scraper.find_advertisements()
scraper.create_json()


