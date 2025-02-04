# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class HomeItems(scrapy.Item):
    platform = scrapy.Field()
    image = scrapy.Field()
    price = scrapy.Field()
    short_desc = scrapy.Field()
    address = scrapy.Field()
    rooms = scrapy.Field()
    surface = scrapy.Field()
    price_per_m = scrapy.Field()
    floor = scrapy.Field()
    seller = scrapy.Field()
    link = scrapy.Field()
    currency = scrapy.Field()
    district = scrapy.Field()

def yield_item_with_defaults(item: scrapy.Item):
    for field_name in item.fields:
        value = item.get(field_name)
        if value is None or str(value).strip() == "":
            item[field_name] = None
    yield item

class ScrapersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
