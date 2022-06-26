import scrapy


class JacksonvilleSpider(scrapy.Spider):
    name = 'jacksonville'
    allowed_domains = ['www.zillow.com']
    start_urls = ['http://www.zillow.com/']

    def parse(self, response):
        pass
