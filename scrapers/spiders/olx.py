
import scrapy
import logging
import json
import re

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
        script_content = response.css("#olx-init-config::text").get()
        parsed_state = self.extract_prerendered_state(script_content)
        offers = self.extract_offers(parsed_state)
        print(json.dumps(offers, indent=4))
        with open('olx.json', 'w') as f:
            json.dump(offers, f)
        
        
    def extract_prerendered_state(self, script_content):
        patterns = [
            r'window\.__PRERENDERED_STATE__\s*=\s*(["\'])(.*?)\1\s*;'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, script_content, re.DOTALL)
            if match:
                escaped_json = match.group(2)
                
                try:
                    unescaped_json = escaped_json.replace('\\"', '"') \
                                                .replace("\\'", '"') \
                                                .replace('\\\\', '\\')
                    
                    parsed_data = json.loads(unescaped_json)
                    
                    return parsed_data
                
                except json.JSONDecodeError:
                    try:
                        # If direct parsing fails, try parsing the raw escaped string
                        parsed_data = json.loads(escaped_json)
                        return parsed_data
                    except json.JSONDecodeError as e:
                        print(f"Parsing error: {e}")
                        print(f"Problematic string: {escaped_json}")
        
        raise ValueError("Could not find and parse configuration")

    def extract_offers(self, json_data):
        try:
            ads_list = json_data.get('listing', {}).get('listing', {}).get('ads', []),

            if ads_list:
                return ads_list
            
            return []
        
        except Exception as e:
            print(f"Error extracting ads: {e}")
            return []

 ###### to be removed if up works

    def parse_old(self, response):

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
            _district = listing.css('div > div > div:nth-of-type(2) > div:nth-of-type(3) > p::text').get()
            details_per_m2 = listing.css('div > div > div:nth-of-type(2) > div:nth-of-type(3) > div > span::text').get()

            if _district is None:
                continue
            if "otodom.pl" in link:
                continue # skip crosslisted listings for now as the ones on olx have less info
            else:
                link = 'https://www.olx.pl' + link
            
            district = _district.split(' -')[0].split(', ')[1]
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
            result['platform'] = 'olx' # TODO - different platform for otodom crosslistings
            result['link'] = link
            result['image'] = image
            result['short_desc'] = short_desc
            result['price'] = price
            result['district'] = district
            result['currency'] = currency
            result['surface'] = surface
            result['price_per_m'] = price_per_m

            results.append(result)

        logging.info(f"Found {len(results)} listings on page {response.url}")
        for result in results:
            yield from yield_item_with_defaults(result)

    def _errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))