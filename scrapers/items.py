# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapers.models import OlxListing, OtodomListing
from sqlalchemy import inspect

# Dynamically create a Scrapy Item class from a SQLAlchemy model
def create_model_item(model_class):
    fields = {}
    for column in inspect(model_class).columns:
        fields[column.name] = Field()
    
    return type(f"{model_class.__name__}Item", (Item,), fields)

OlxListingItem = create_model_item(OlxListing)
OtodomListingItem = create_model_item(OtodomListing)

def yield_item_with_defaults(item_dict, model_item_class):
    model_item = model_item_class()
    for key, value in item_dict.items():
        if value is None or str(value).strip() == "":
            model_item[key] = None
        else:
            model_item[key] = value
    
    yield model_item
