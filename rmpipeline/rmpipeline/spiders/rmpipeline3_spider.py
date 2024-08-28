import scrapy
import yaml
import os
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class RMSpider(scrapy.Spider):
    name = "rmpipeline3_spider"
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'rmpipeline.middlewares.CustomSeleniumMiddleware': 800,
        },
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_ARGUMENTS': ['--headless'],
    }
    
    def __init__(self, *args, **kwargs):
        super(RMSpider, self).__init__(*args, **kwargs)

        # Load configuration from config.yml
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)
        
        self.postcodes = self.config.get('postcodes', [])
        self.radius = self.config.get('radius')
        self.results_limit = 300
        self.results_per_page = 24
        self.base_url = "https://www.rightmove.co.uk/property-for-sale/find.html"

    def start_requests(self):
        total_pages = (self.results_limit + self.results_per_page - 1) // self.results_per_page  
        
        for postcode in self.postcodes:
            location_identifier = f"POSTCODE%5E{postcode.replace(' ', '')}"
            for page in range(total_pages):
                index = page * self.results_per_page
                url = f"{self.base_url}?locationIdentifier={location_identifier}&radius={self.radius}&sortType=6&index={index}&includeSSTC=false"
                self.logger.info(f"Requesting URL: {url}")
                yield SeleniumRequest(url=url, callback=self.parse, wait_time=3, dont_filter=True, meta={'index': index})

    def parse(self, response):
        index = response.meta.get('index')
        driver = response.meta.get('driver')
        yield from self.parse_listings(response, index, driver)  

    def parse_listings(self, response, index, driver):
        if response.status == 400:
            self.logger.error(f"Received a 400 error for URL: {response.url}")
            return

        property_links = response.css('div.propertyCard a.propertyCard-link::attr(href)').getall()
        self.logger.info(f"Found {len(property_links)} property links on the page")
        for link in property_links:
            full_link = response.urljoin(link)
            self.logger.info(f"Following property link: {full_link}")
            yield SeleniumRequest(url=full_link, callback=self.parse_property, wait_time=3, meta={'index': index, 'driver': driver})

    def parse_property(self, response):
        driver = response.meta.get('driver')
        if not driver:
            self.logger.error("Driver not found in response meta")
            return

        broadband_speed = None
        sale_history = None
        property_price = None
        deposit = None
        annual_interest_percentage = None
        repayment_period = None

        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Broadband speed')]"))
            ).click()
            broadband_speed = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#root > main > div > div.WJG_W7faYk84nW-6sCBVi > div > div:nth-child(15) > div > div.zZPmRZvpgW4UbacqIAcb > div._33b8ehG4PUCTBrpLXiFNqe > div._1sk-rdoF8wJ5cv4soguG60 > div > div > div > p._3FgmLiyUP1vZHVPTaAmTzk'))
            ).text
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(f"Error finding broadband speed: {e}")

        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Sale history')]"))
            ).click()
            sale_history_rows = WebDriverWait(driver, 10).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'table._21YyDQGl_UcQfKChdb4iko tbody tr'))
            )
            sale_history = [{'year_sold': row.find_element_by_css_selector('td:nth-child(1)').text, 'sold_price': row.find_element_by_css_selector('td:nth-child(2) div span').text} for row in sale_history_rows]
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(f"Error finding sale history: {e}")

        try:
            property_price = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#property-price'))
            ).text
            deposit = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#property-deposit'))
            ).text
            annual_interest_percentage = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#property-interest'))
            ).text
            repayment_period = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#property-term'))
            ).text
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(f"Error extracting mortgage details: {e}")

        yield {
            'broadband_speed': broadband_speed,
            'sale_history': sale_history,
            'mortgage_details': {
                'property_price': property_price,
                'deposit': deposit,
                'annual_interest_percentage': annual_interest_percentage,
                'repayment_period': repayment_period
            }
        }
