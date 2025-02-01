from sqlalchemy import Column, Integer, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.engine.url import URL
from datetime import datetime
from shared.database import Base

class ApartmentListing(Base):
    __tablename__ = 'apartment_listings'

    id = Column(Integer, primary_key=True)
    # Modify these fields based on your spider's items
    link = Column(String(255))
    image = Column(Text)
    price = Column(Numeric(12, 2))
    address = Column(String(255))
    rooms = Column(String(25))
    surface = Column(Numeric(4, 2))
    price_per_m = Column(Numeric(6, 2))
    floor = Column(Integer)
    seller = Column(String(255))
    short_desc = Column(String(255))
    currency = Column(String(3))
    district = Column(String(50))
    date_last_seen = Column(DateTime)