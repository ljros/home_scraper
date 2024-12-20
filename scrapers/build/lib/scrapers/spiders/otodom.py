
import scrapy
import logging

from ..items import HomeItems

class OtodomSpider(scrapy.Spider):

    def __init__(self, *args, **kwargs):
        super(OtodomSpider, self).__init__(*args, **kwargs)
        # self.sellers = ast.literal_eval(usernames)

        # self.seller_url_gen = ('https://www.ebay.{}/fdbk/feedback_profile/{}'.format(self.domain_, quote_plus(seller)) for seller in self.sellers)
        self.start_urls = ['https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa/warszawa/warszawa']

    handle_httpstatus_list = [410, 307, 301]
    name = 'otodom'
    allowed_domains = ['otodom.pl']

    def parse(self, response):
        #feedbacks first

        if response.status == 307:
            return

        results = []

        # scrapy shell -s USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36" "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa/warszawa/warszawa"

        # pos_1 = response.css('[data-test-id="rating-count-1"]::text').get()
        listings = response.css('div[data-cy="search.listing.organic"] ul li')
        for listing in listings:
            image, price, short_desc, address, rooms, surface, price_per_m, floor, seller = '','','','','','','','',''
            if not (listing.css("article").get()):
                continue

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
                price_per_m = " ".join([details_dd[0].replace("\xa0129\xa0", ""), details_dd[2]])
                del details_dd[0:3]
            if 'Piętro' in details_dt:
                floor = details_dd[0]
                del details_dd[0]

            # for i, detail in enumerate(details_dt):
            #     rooms = details_dd[i] if detail == 'Liczba pokoi' else ""
            #     surface = details_dd[i] if detail == 'Powierzchnia' else ""
            #     price_per_m = details_dd[i] if detail == 'Cena za metr kwadratowy' else ""
            #     floor = details_dd[i] if detail == 'Piętro' else ""

            seller = listing.css(' article > section > div:nth-of-type(2) > div:nth-of-type(5) > div > div::text').get()

            result = HomeItems()
            result['image'] = image
            result['price'] = price
            result['short_desc'] = short_desc
            result['address'] = address
            result['rooms'] = rooms
            result['surface'] = surface
            result['price_per_m'] = price_per_m
            result['floor'] = floor
            result['seller'] = seller

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





# ---------------------------------------

    def pass_(self):
        #test
        # empty = True
        # for x in results.items():
        #     if x != "" and x != 0:
        #         empty = False
        #         break
        # if not empty:
        #     yield {k: v for k, v in results.items() if v}
        # table royal
        # // *[ @ id = "vi-ship-maincntr"] / div / div / div / div[1] / div[4] / table / tbody
        # pod tym są itemy
        # // *[ @ id = "ListViewInner"]
        #testend



        response=''
        # return self._return(results)
        # end changes

        username = response.css(".mbg-id::text").extract_first()
        business_name = response.css("span#business_name + span::text").extract_first()
        first = response.css("span#first_name + span::text").extract_first()
        last = response.css("span#last_name + span::text").extract_first()
        email = response.css("span#email + span::text").extract_first()
        phone = response.css("span#phone_number + span::text").extract_first()
        listings = response.css(".sell_count a::text").extract_first()
        address = self._get_address(response)

        if not phone:
            phone = self._get_phone_from_desc(response)
        if not email:
            email = self._get_email_from_desc(response)

        results = EbayItems()
        results['username'] = username
        results['business_name'] = business_name
        results['first'] = first
        results['last'] = last
        results['email'] = email
        results['address'] = address
        results['phone'] = phone
        results['listings'] = listings

        # url = 'https://www.ebay.co.uk/fdbk/feedback_profile/' + str(results['username'])
        url = 'https://www.ebay.{}/fdbk/feedback_profile/{}'.format(self.domain_, str(results['username']))

        yield scrapy.Request(url=url,
                             callback=self._request_feedbacks,
                             errback=self._errback_httpbin,
                             meta=dict(results=results))

