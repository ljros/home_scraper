
import scrapy
import logging

from ..items import HomeItems

class OtodomSpider(scrapy.Spider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_urls = ['https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa/warszawa/warszawa']

    handle_httpstatus_list = [410, 307, 301]
    name = 'otodom'
    allowed_domains = ['otodom.pl']

    def parse(self, response):
        #feedbacks first

        if response.status == 307:
            return

        results = []


        listings = response.css('div[data-cy="search.listing.organic"] ul li')
        for listing in listings:
            link, image, price, short_desc, address, rooms, surface, price_per_m, floor, seller = '','','','','','','','','',''
            if not (listing.css("article").get()):
                continue
            
            link = listing.css('article > section > div:nth-of-type(2) >  a::attr(href)').get()
            image = listing.css('article > section > div:nth-of-type(1) > div > div > div > div > div > div > div:nth-of-type(1) > a > img::attr(src)').getall()
            price = listing.css('article > section > div:nth-of-type(2) > div:nth-of-type(1) > span::text').get()
            short_desc = listing.css('article > section > div:nth-of-type(2) > a > p::text').get()
            address = listing.css('article > section > div:nth-of-type(2) > div:nth-of-type(2) > p::text').get()

            details_dt = listing.css('article > section > div:nth-of-type(2) > div:nth-of-type(3) > dl > dt::text').getall()
            details_dd = listing.css('article > section > div:nth-of-type(2) > div:nth-of-type(3) > dl > dd::text').getall()

            logging.info(details_dt)
            logging.info(details_dd)

            if 'Liczba pokoi' in details_dt:
                rooms = details_dd[0]
                del details_dd[0]
            if 'Powierzchnia' in details_dt:
                surface = " ".join([details_dd[0], details_dd[1], details_dd[2]])
                del details_dd[0:3]
            if 'Cena za metr kwadratowy' in details_dt:
                price_per_m = " ".join([details_dd[0], details_dd[2]]) # .replace("\xa0129\xa0", "")
                del details_dd[0:3]
            if 'Piętro' in details_dt:
                floor = details_dd[0]
                del details_dd[0]
            if link:
                link = 'https://www.otodom.pl' + link

            seller = listing.css(' article > section > div:nth-of-type(2) > div:nth-of-type(5) > div > div::text').get()

            result = HomeItems()
            result['platform'] = 'otodom'
            result['image'] = image
            result['price'] = price
            result['short_desc'] = short_desc
            result['address'] = address
            result['rooms'] = rooms
            result['surface'] = surface
            result['price_per_m'] = price_per_m
            result['floor'] = floor
            result['seller'] = seller
            result['link'] = link

            results.append(result)


        for result in results:
            if result:
                yield from self._return(result)


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
            yield {k: v for k, v in results.items() if v}