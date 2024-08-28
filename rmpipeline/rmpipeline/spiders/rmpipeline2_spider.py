import scrapy
import yaml
import os
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class RMSpider(scrapy.Spider):
    name = "rmpipeline2_spider"

    def __init__(self, *args, **kwargs):
        super(RMSpider, self).__init__(*args, **kwargs)

        # Load configuration from config.yml
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)
        
        self.postcodes = self.config.get('postcodes', [])
        self.radius = self.config.get('radius', [])
        self.results_limit = 300
        self.results_per_page = 24
        self.base_url = "https://www.rightmove.co.uk/property-for-sale/find.html"

    def start_requests(self):
        for postcode in self.postcodes:
            location_identifier = f"POSTCODE%5E{postcode.replace(' ', '')}"
            total_pages = (self.results_limit + self.results_per_page - 1) // self.results_per_page
            
            for page in range(total_pages):
                index = page * self.results_per_page
                url = f"{self.base_url}?locationIdentifier={location_identifier}&radius={self.radius}&sortType=6&index={index}&includeSSTC=false"
                self.logger.info(f"Requesting URL: {url}")
                yield SeleniumRequest(url=url, callback=self.parse_listings)

    def parse_listings(self, response):
        if response.status == 400:
            self.logger.error(f"Received a 400 error for URL: {response.url}")
            return

        property_links = response.css('div.propertyCard a.propertyCard-link::attr(href)').getall()
        self.logger.info(f"Found {len(property_links)} property links on the page")
        for link in property_links:
            full_link = response.urljoin(link)
            self.logger.info(f"Following property link: {full_link}")
            yield SeleniumRequest(url=full_link, callback=self.parse_property)

    def parse_property(self, response):
        stations = []

        # For station information
        station_elements = response.css('div#Stations-panel ul._2f-e_tRT-PqO8w8MBRckcn li')
        for station in station_elements:
            station_name = station.css('span.cGDiWU3FlTjqSs-F1LwK4::text').get()
            station_distance = station.css('span._1ZY603T1ryTT3dMgGkM7Lg::text').get()
            if station_name and station_distance:
                stations.append({
                    "name": station_name.strip(),
                    "distance_in_miles": float(station_distance.strip().replace(" miles", ""))
                })

        # Click on the 'Schools' tab to reveal the schools information
        driver = response.meta['driver']
        self.dismiss_cookie_consent(driver)

        try:
            schools_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'Schools-button'))
            )
            schools_button.click()
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'Schools-panel'))
            )
        except Exception as e:
            self.logger.error(f"Error clicking on Schools tab: {e}")
            return

        # For school information
        schools = self.extract_schools(driver)

        self.logger.info(f"Scraped property with {len(stations)} stations and {len(schools)} schools")

        # Yield the data to the pipeline
        yield {
            "stations": stations,
            "schools": schools
        }

    def dismiss_cookie_consent(self, driver):
        try:
            dismiss_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.onetrust-close-btn-handler'))
            )
            dismiss_button.click()
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, '.onetrust-pc-dark-filter'))
            )
        except Exception as e:
            self.logger.error(f"Error dismissing overlay: {e}")

    def extract_schools(self, driver):
        schools = []

        try:
            school_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#Schools-panel ul > li'))
            )
            self.logger.info(f"Found {len(school_elements)} school elements")

            for school in school_elements:
                school_name = school.find_element(By.CSS_SELECTOR, 'a > div._3vnejYOr9kDUWyuIoSC5wj > div > div.m-sPgjdhogr7nMcdJWvco > span').text
                school_type = school.find_element(By.CSS_SELECTOR, 'a > div._3vnejYOr9kDUWyuIoSC5wj > div > div.m-sPgjdhogr7nMcdJWvco > div > span:nth-child(1)').text
                school_ranking = school.find_element(By.CSS_SELECTOR, 'a > div._3vnejYOr9kDUWyuIoSC5wj > div > div.m-sPgjdhogr7nMcdJWvco > div > span:nth-child(2)').text
                school_distance = school.find_element(By.CSS_SELECTOR, 'a > div._3vnejYOr9kDUWyuIoSC5wj > div > div._3c74qVLIY4CQEzQmQ80PAU').text

                if school_name and school_type and school_ranking and school_distance:
                    schools.append({
                        "name": school_name.strip(),
                        "type": school_type.strip(),
                        "ranking": school_ranking.strip(),
                        "distance_in_miles": float(school_distance.strip().replace(" miles", ""))
                    })
        except Exception as e:
            self.logger.error(f"Error extracting schools information: {e}")

        return schools
