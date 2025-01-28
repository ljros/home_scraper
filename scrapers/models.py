from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from datetime import datetime

Base = declarative_base()

class ScrapedItem(Base):
    __tablename__ = 'scraped_items'

    id = Column(Integer, primary_key=True)
    # Modify these fields based on your spider's items
    image = Column(String)
    price = Column(String)
    short_desc = Column(String)
    address = Column(String)
    rooms = Column(String)
    surface = Column(String)
    price_per_m = Column(String)
    floor = Column(String)
    seller = Column(String)
    link = Column(String)

    # scraped_at = Column(DateTime, default=datetime.utcnow)

