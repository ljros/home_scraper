from urllib.parse import quote_plus
import logging
import scrapy
import ast
import re
from ..items import EbayItems


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
        neg_1 = response.css('[data-test-id="rating-count-7"]::text').get()
        pos_6 = response.css('[data-test-id="rating-count-2"]::text').get()
        neu_6 = response.css('[data-test-id="rating-count-5"]::text').get()
        neg_6 = response.css('[data-test-id="rating-count-8"]::text').get()
        pos_12 = response.css('[data-test-id="rating-count-3"]::text').get()
        neu_12 = response.css('[data-test-id="rating-count-6"]::text').get()
        neg_12 = response.css('[data-test-id="rating-count-9"]::text').get()

        results['pos_1'] = pos_1
        results['neu_1'] = neu_1
        results['neg_1'] = neg_1
        results['pos_6'] = pos_6
        results['neu_6'] = neu_6
        results['neg_6'] = neg_6
        results['pos_12'] = pos_12
        results['neu_12'] = neu_12
        results['neg_12'] = neg_12


        data = response.xpath('//div[@class = "userTopLine"]/a/@href').getall()
        username, store_name = "",""
        for item in data:
            if '/usr' in item:
                username = item.split('/')[-1]
            elif 'stores.' in item:
                store_name = item.split('/')[-1]

        results['username'] = username
        results['store_name'] = store_name

        if store_name:
            url = 'https://www.ebay.co.uk/str/{}'.format(str(results['store_name']))
            yield scrapy.Request(url=url,
                                 headers={'X-Crawlera-Max-Retries': 3},
                                 callback=self._request_store,
                                 errback=self._errback_httpbin,
                                 meta=dict(results=results))
        elif username:
            url = 'https://www.ebay.co.uk/usr/{}'.format(str(results['username']))
            yield scrapy.Request(url=url,
                                 headers={'X-Crawlera-Max-Retries': 3},
                                 callback=self._request_store,
                                 errback=self._errback_httpbin,
                                 meta=dict(results=results))
            # url = 'https://www.ebay/.{}/sch/{}/m.html'.format(self.domain_, str(results['username']))
            # yield scrapy.Request(url=url,
            #                      callback=self._request_live_listings,
            #                      errback=self._errback_httpbin,
            #                      meta=dict(results=results))
        else:
            yield from self._return(results)


    def _request_store(self, response):
        results = response.meta['results']

        business_name_, first_, last_, address_, phone_, email_ = 'Business name:\xa0', 'First name:\xa0', 'Surname:\xa0', 'Address:\xa0', 'Phone number:\xa0', 'Email:\xa0'
        store_origin_, user_age_, username_ = 'Location:\xa0', 'Member since:\xa0', 'Seller:\xa0'
        business_name, first, last, address, phone, email, store_origin, user_age, username = "","","","","","","","",""

        business_info_key = response.xpath('//*[@class="str-about-description__seller-info"]/span/span[1]/text()').getall()
        business_info = response.xpath('//*[@class="str-about-description__seller-info"]/span/span[2]/text()').getall()

        business_details_key = response.xpath('//*[@class="str-business-details__seller-info"]/span/span[1]/text()').getall()
        business_details = response.xpath('//*[@class="str-business-details__seller-info"]/span/span[2]/text()').getall()

        logging.info(business_info_key)
        logging.info(business_info)
        logging.info(business_details_key)
        logging.info(business_details)
        if store_origin_ in business_info_key:
            store_origin = business_info[business_info_key.index(store_origin_)]
        if user_age_ in business_info_key:
            user_age = business_info[business_info_key.index(user_age_)]
        # if username_ in business_info_key:
        #     username = business_info[business_info_key.index(username_)]

        if business_name_ in business_details_key:
            business_name = business_details[business_details_key.index(business_name_)]
        if first_ in business_details_key:
            first = business_details[business_details_key.index(first_)]
        if last_ in business_details_key:
            last = business_details[business_details_key.index(last_)]
        if address_ in business_details_key:
            address = business_details[business_details_key.index(address_)]
        if phone_ in business_details_key:
            phone = business_details[business_details_key.index(phone_)]
        if email_ in business_details_key:
            email = business_details[business_details_key.index(email_)]

        # shop_name_ = response.xpath('//div[@class = "str-seller-card__store-name"] // a / @href').get()
        # shop_name = shop_name_.split('/')[-1]

        # results['shop_name'] = shop_name
        results['store_origin'] = store_origin
        results['user_age'] = user_age
        # results['username'] = username
        results['business_name'] = business_name
        results['first'] = first
        results['last'] = last
        results['address'] = address
        results['phone'] = phone
        results['email'] = email

        # url = 'https://www.ebay.{}/sch/{}/m.html'.format(self.domain_, str(results['username']))
        url = 'https://www.ebay.{}/sch/i.html?_ssn={}'.format(self.domain_, str(results['username']))

        yield scrapy.Request(url=url,
                             callback=self._request_live_listings,
                             errback=self._errback_httpbin,
                             meta=dict(results=results))


    def _request_live_listings(self, response):
        results = response.meta['results']

        listings = response.xpath('// *[ @ id = "cbel/m"] / div[3] / span[1]/text()').get()
        category = response.xpath('// div[@class="catsgroup"]/div[@class="cat-t"]/a/text()').get()

        listings_raw = response.xpath('// h1[@class = "srp-controls__count-heading"]/text()').get()
        listings_split = [int(s) for s in listings_raw.split() if s.isdigit()]
        listings = ''.join(str(e) for e in listings_split)
        category = response.xpath('//*[@id="x-refine__group__0"]/ul/li/ul/li[1]/a/span/text()').get()

        results['listings'] = listings
        results['category'] = category

        item = response.xpath('//*[@id="srp-river-results"]/ul/li[1]/div/div[1]/div/a/@href')

        if listings and listings != '0':
            url = item.get().split('?')[0]
            yield scrapy.Request(url=url,
                                 callback=self._request_vat_royal,
                                 errback=self._errback_httpbin,
                                 meta=dict(results=results))
        else:
            yield from self._return(results)

    def _request_vat_royal(self, response):
        results = response.meta['results']

        vat = response.xpath(("//ul[contains(concat(' ',normalize-space(@class),' '),'ux-section--vatInformation')] // span / text()")).get()
        shipping_methods = response.xpath("//table[contains(concat(' ',normalize-space(@class),' '),'ux-table-section-with-hints--shippingTable')] // td[4] / span / text()").getall()
        royal_mail = ""
        for shipping in shipping_methods:
            if "Royal Mail" in shipping:
                royal_mail = "True"
                break
        if not royal_mail:
            royal_mail = "False"

        results['vat'] = vat
        results['royal_mail'] = royal_mail

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

    def _get_phone_from_desc(self, response):
        desc = response.css("#user_bio > div.show_value > div > h2::text").extract_first()
        if desc:
            p = re.compile(r'((\(\d{3}\) ?)|(\d{3}-))?\d{3}-\d{4}')
            res = p.search(desc)
            if res:
                self.log('found phone')
                return res.group()
        return ""

    def _get_email_from_desc(self, response):
        desc = response.css("#user_bio > div.show_value > div > h2::text").extract_first()
        if desc:
            p = re.compile(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)')
            res = p.search(desc)
            if res:
                self.log('found email')
                return res.group()
        return ""

    def _get_address(self, response):
        addresses = response.css("span#address ~ span ::text").extract()
        addresses = ''.join(addresses).replace(',', ';')
        return " ".join(addresses.split())



    def _request_vat(self, response):
        results = response.meta['results']

        vat = response.css('.vat-number div::text').extract_first()
        vat = response.css('.ux-unordered-list__item > span:nth-child(1)::text').extract_first()

        results['vat'] = vat

        return self._return(results)
        # yield {k: v for k, v in results.items() if v is not ""}

