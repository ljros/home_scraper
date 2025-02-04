
import scrapy
import logging

from ..items import HomeItems, yield_item_with_defaults

class OlxSpider(scrapy.Spider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_urls = ['https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/warszawa/']

    handle_httpstatus_list = [410, 307, 301]
    name = 'olx'
    allowed_domains = ['olx.pl']

    def parse(self, response):

        if response.status == 307:
            return

        results = []

        listings = response.css('div.listing-grid-container > div:nth-of-type(2) div')
        for listing in listings:
            # skip promoted listings
            if not listing.css('::attr(id)').get() or '-ad-' in listing.css('::attr(id)').get(): 
                 continue


            link = listing.css('div > div > div:nth-of-type(1) >  a::attr(href)').get()
            image = listing.css('div > div > div:nth-of-type(1) > a > div > div > img::attr(src)').get()
            short_desc = listing.css('div > div > div:nth-of-type(2) > div > a > h4::text').get()
            price = listing.css('div > div > div:nth-of-type(2) > div > p::text').get()
            address = listing.css('div > div > div:nth-of-type(2) > div:nth-of-type(3) > p::text').get()
            details_per_m2 = listing.css('div > div > div:nth-of-type(2) > div:nth-of-type(3) > div > span::text').get()

            if address is None:
                continue
            
            district = address.split(' -')[0].split(', ')[1]
            surface = details_per_m2.split(' - ')[0]
            price_per_m = details_per_m2.split(' - ')[1]

            if "zł" in price:
                price = price.replace("zł", "").replace(" ", "").replace(",", ".")
                currency = "PLN"
            else:
                currency = price.split(" ")[-1]
                price = "".join(price.split(" ")[:-1].replace(",", "."))

            surface = surface.replace(" m²", "").replace(",", ".")
            price_per_m = price_per_m.replace(" zł/m²", "").replace(",", ".")

            result = HomeItems()
            result['platform'] = 'olx'
            result['link'] = link
            result['image'] = image
            result['short_desc'] = short_desc
            result['price'] = price
            result['address'] = address
            result['district'] = district
            result['currency'] = currency
            result['surface'] = surface
            result['price_per_m'] = price_per_m

            # result['rooms'] = ""
            # result['floor'] = ""
            # result['seller'] = ""

            results.append(result)

        logging.info(f"Found {len(results)} listings on page {response.url}")
        for result in results:
            # yield result 
            # yield from self._return(result)
            yield from yield_item_with_defaults(result)

    def _errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

    def _return(self, results):
        empty = True
        for x in results.items():
            if x != "" and x != 0:
                empty = False
                break
        if not empty:
            yield {k: v for k, v in results.items()}