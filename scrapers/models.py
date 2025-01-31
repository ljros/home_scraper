# from sqlalchemy import create_engine, Column, Integer, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.engine.url import URL
from datetime import datetime
from shared.database import Base

class ApartmentListing(Base):
    __tablename__ = 'apartment_listings'

    id = Column(Integer, primary_key=True)
    # Modify these fields based on your spider's items
    image = Column(String)
    price = Column(String(50))
    short_desc = Column(String)
    address = Column(String(255))
    rooms = Column(String(25))
    surface = Column(String(25))
    price_per_m = Column(String(25))
    floor = Column(String(25))
    seller = Column(String(255))
    link = Column(String(255))
    date_created = Column(DateTime)
    date_last_seen = Column(DateTime)
