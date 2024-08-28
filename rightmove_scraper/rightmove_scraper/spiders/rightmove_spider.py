import scrapy

class RightmoveSpider(scrapy.Spider):
    name = "rightmove_spider"
    allowed_domains = ["rightmove.co.uk"]
    
    start_urls = [
        f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=POSTCODE%5E573703&radius=3.0&sortType=6&index={i*24}&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=" 
        for i in range(34)
    ]
    
    def parse(self, response):
        for listing in response.css('div.propertyCard'):
            yield {
                'listing_name': listing.css('h2.propertyCard-title::text').get().strip(),
                'scraped_url': response.url
            }

