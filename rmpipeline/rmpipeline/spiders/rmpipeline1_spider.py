import scrapy
import yaml
import os
import logging
from datetime import datetime

class RMSpider(scrapy.Spider):
    name = 'rmpipeline1_spider'
    allowed_domains = ['rightmove.co.uk']
    
    def __init__(self, *args, **kwargs):
        super(RMSpider, self).__init__(*args, **kwargs)

        # Load configuration from config.yml
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)
        
        self.postcodes = self.config.get('postcodes', [])
        self.radius = self.config.get('radius')
        self.max_results = 300
        self.total_results = 0

        self.start_urls = []
        for postcode in self.postcodes:
            self.start_urls.extend([
                f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=POSTCODE%5E{postcode.replace(' ', '')}&radius={self.radius}&sortType=6&index={i*24}&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=" 
                for i in range((self.max_results + 23) // 24)
            ])
    
    def parse(self, response):
        property_urls = response.css('a.propertyCard-link::attr(href)').extract()
        for url in property_urls:
            if self.total_results < self.max_results:
                full_url = response.urljoin(url)
                yield scrapy.Request(url=full_url, callback=self.parse_property)
                self.total_results += 1
            else:
                break

        if self.total_results < self.max_results:
            next_page = response.css('a.pagination-direction--next::attr(href)').get()
            if next_page:
                yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)

    def parse_property(self, response):
        listing_name = response.css('h1::text').get()
        price_qualifier = response.css('div[data-testid="priceQualifier"]::text').get()
        price = response.css('span:contains("£")::text').get()
        added_date = response.css('div:contains("Added on"), div:contains("Reduced on")::text').re_first(r'(\d{2}/\d{2}/\d{4})')
        property_type = response.css('p._1hV1kqpVceE9m-QrX_hWDN::text').get()
        bedrooms = response.css('#info-reel > div:nth-child(2) > dd > span p::text').get()
        bathrooms = response.css('#info-reel > div:nth-child(3) > dd > span p::text').get()
        property_size = response.css('#info-reel > div:nth-child(4) > dd > span p::text').get()
        tenure = response.css('#info-reel > div:nth-child(5) > dd > span p::text').get()
        key_features = response.css('#root > main > div > div.WJG_W7faYk84nW-6sCBVi > div > article:nth-child(5) > ul li::text').getall()
        property_description = ' '.join(response.css('#root > main > div > div.WJG_W7faYk84nW-6sCBVi > div > article:nth-child(5) > div.OD0O7FWw1TjbTD4sdRi1_ > div > div *::text').getall()).strip()
        epc_rating = response.css('a._1TPMspLiJy32yox8cn32Nw::text').get()
        epc_rating_url = response.css('a._1TPMspLiJy32yox8cn32Nw::attr(href)').get()
        council_tax = response.css('#root > main > div > div.WJG_W7faYk84nW-6sCBVi > div > article:nth-child(5) > div._2lgGht40HlBBIUj6Oi0eW1 > div > p::text').get()

        # Debugging logs
        #logging.info(f'Listing name: {listing_name}')
        #logging.info(f'Price qualifier: {price_qualifier}')
        logging.info(f'Price: {price}')
        #logging.info(f'Added date: {added_date}')
        #logging.info(f'Property type: {property_type}')
        #logging.info(f'Bedrooms: {bedrooms}')
        #logging.info(f'Bathrooms: {bathrooms}')
        #logging.info(f'Property size: {property_size}')
        #logging.info(f'Tenure: {tenure}')
        #logging.info(f'Key features: {key_features}')
        #logging.info(f'Property description: {property_description}')
        logging.info(f'EPC rating: {epc_rating}')
        logging.info(f'EPC rating URL: {epc_rating_url}')
        #logging.info(f'Council tax: {council_tax}')

        yield {
            'listing_name': listing_name.strip() if listing_name else None,
            'listing_url': response.url,
            'source': 'RM',
            'price_qualifier': price_qualifier.strip() if price_qualifier else None,
            'price': price.strip() if price else None,
            'added_date': added_date.strip() if added_date else None,
            'property_type': property_type.strip() if property_type else None,
            'bedrooms': bedrooms.strip() if bedrooms else None,
            'bathrooms': bathrooms.strip() if bathrooms else None,
            'property_size': {
                'value': property_size.strip() if property_size else None,
                'unit': 'sq. ft.'
            },
            'tenure': tenure.strip() if tenure else None,
            'key_features': key_features,
            'property_description': property_description.strip() if property_description else None,
            'energy_performance_certificates': {
                'rating': epc_rating.strip() if epc_rating else None,
                'rating_url': epc_rating_url
            },
            'council_tax': council_tax.strip() if council_tax else None,
            '_extracted_datetime': datetime.now().isoformat(),
            '_extracted_date': '2024-06-07',
            '_extracted_postcode': self.postcode,
            '_extracted_radius_in_miles': self.radius,
            '_extracted_listing_type': 'buy'
        }
