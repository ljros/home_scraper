
import scrapy

class EbayScraperSpider(scrapy.Spider):

    def __init__(self, usernames, domain, *args, **kwargs):
        super(EbayScraperSpider, self).__init__(*args, **kwargs)
        self.sellers = ast.literal_eval(usernames)

        domain = domain.replace("'", "")
        domain = domain.replace('"', "")
        if domain.lower() == 'uk':
            domain = 'co.uk'
        self.domain_ = domain.lower()
        self.seller_url_gen = ('https://www.ebay.{}/fdbk/feedback_profile/{}'.format(self.domain_, quote_plus(seller)) for seller in self.sellers)
        # self.seller_url_gen = ('https://www.ebay.co.uk/usr/{}'.format(quote_plus(seller)) for seller in self.sellers)
        # self.seller_url_gen = ('https://www.ebay.{}/sch/{}/m.html?_nkw=&_armrs=1&_ipg=x'.format(domain.lower(), quote_plus(seller)) for seller in self.sellers)
        self.start_urls = self.seller_url_gen

    # start_urls = ['https://ebay.co.uk/usr/{}']
    handle_httpstatus_list = [410, 307, 301]
    name = 'ebay_scraper'
    allowed_domains = ['ebay.co', 'ebay.co.uk', 'www.ebay.co.uk', 'ebay.de', 'ebay.com', 'ebay.fr', 'ebay.es',
                       'ebay.it', 'ebay.be', 'ebay.nl', 'ebay.pl', 'ebay.ie', 'ebay.at', 'ebay.com.au', 'ebay.ch']

    def parse(self, response):
        #feedbacks first

        if response.status == 307:
            return

        results = EbayItems()

        pos_1 = response.css('[data-test-id="rating-count-1"]::text').get()
        neu_1 = response.css('[data-test-id="rating-count-4"]::text').get()


        results['pos_1'] = pos_1
        results['neu_1'] = neu_1

        url = 'https://www.ebay.co.uk/str/{}'.format(str(results['store_name']))
        yield scrapy.Request(url=url,
                             headers={'X-Crawlera-Max-Retries': 3},
                             callback=self._request_store,
                             errback=self._errback_httpbin,
                             meta=dict(results=results))
        else:
            yield from self._return(results)


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

