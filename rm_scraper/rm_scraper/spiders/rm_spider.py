import scrapy

class RmSpider(scrapy.Spider):
    name = 'rm_spider'
    allowed_domains = ['rightmove.co.uk']
    start_urls = [
        'https://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&locationIdentifier=POSTCODE%5E573703&insId=1&radius=3.0&minPrice=&maxPrice=&minBedrooms=&maxBedrooms=&displayPropertyType=&maxDaysSinceAdded=&_includeSSTC=on&sortByPriceDescending=&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&newHome=&auction=false'
    ]

    def parse(self, response):
        for listing in response.css('.propertyCard'):
            listing_name = listing.css('.propertyCard-title::text').get()
            listing_url = response.urljoin(listing.css('a.propertyCard-link::attr(href)').get())
            yield {
                'listing_name': listing_name.strip() if listing_name else None,
                'listing_url': listing_url
            }
        
        # Follow pagination links
        next_page = response.css('a.pagination-direction--next::attr(href)').get()
        if next_page:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
