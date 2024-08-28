import os
from scrapy.http import HtmlResponse
from scrapy_selenium import SeleniumMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class CustomSeleniumMiddleware(SeleniumMiddleware):

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(selenium_driver_arguments=crawler.settings.get('SELENIUM_DRIVER_ARGUMENTS'))
        return middleware

    def __init__(self, selenium_driver_arguments, *args, **kwargs):
        self.selenium_driver_arguments = selenium_driver_arguments
        chrome_service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        for arg in self.selenium_driver_arguments:
            options.add_argument(arg)
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-tools")
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--remote-debugging-port=9230")
        self.driver = webdriver.Chrome(service=chrome_service, options=options)

    def process_request(self, request, spider):
        self.driver.get(request.url)
        # Wait for the property cards to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.propertyCard'))
            )
        except Exception as e:
            spider.logger.error(f"Error waiting for property cards to load: {e}")

        body = self.driver.page_source
        response = HtmlResponse(
            url=self.driver.current_url,
            body=body,
            encoding='utf-8',
            request=request
        )
        # Add the driver to response.meta to use it in the spider
        request.meta['driver'] = self.driver

        return response

    def spider_closed(self, spider):
        self.driver.quit()