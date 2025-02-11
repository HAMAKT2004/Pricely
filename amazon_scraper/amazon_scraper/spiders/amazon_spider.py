import scrapy
from amazon_scraper.items import AmazonScraperItem

class AmazonSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = ["amazon.in"]
    start_urls = ["https://www.amazon.in/s?k=smartphones"]

    def parse(self, response):
        products = response.css('div.s-main-slot div.s-card-container')

        for product in products:
            item = AmazonScraperItem()

            # Extract product name
            item['product_name'] = product.css('span.a-size-medium::text').get()

            # Extract product link
            product_link = product.css('a.a-link-normal::attr(href)').get()
            if product_link:
                item['product_link'] = response.urljoin(product_link)

            # Extract product price
            item['product_price'] = product.css('span.a-price-whole::text').get()

            # Extract product image link
            item['product_image_link'] = product.css('img.s-image::attr(src)').get()

            yield item