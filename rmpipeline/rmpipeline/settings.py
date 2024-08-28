import os
import yaml

BOT_NAME = "rmpipeline"

SPIDER_MODULES = ["rmpipeline.spiders"]
NEWSPIDER_MODULE = "rmpipeline.spiders"

# Enable item pipelines
ITEM_PIPELINES = {
    'rmpipeline.pipelines.JsonWriterPipeline': 800,
}

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, "rmpipeline", "config.yml"), 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)

POSTCODES = cfg['postcodes']

SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_ARGUMENTS = ['--headless', '--disable-dev-shm-usage', '--no-sandbox', '--disable-gpu', '--disable-dev-tools', '--disable-setuid-sandbox', '--start-maximized', '--window-size=1920,1080']

DOWNLOADER_MIDDLEWARES = {
    'rmpipeline.middlewares.CustomSeleniumMiddleware': 800,
    'scrapy_selenium.SeleniumMiddleware': None,   
}
