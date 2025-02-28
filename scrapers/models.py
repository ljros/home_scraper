from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from shared.database import Base

# Define the SQLAlchemy model

class OlxListing(Base):
    __tablename__ = 'olx_listings'

    id = Column(Integer, primary_key=True)

    platform = Column(String(25))
    title = Column(String(255))
    description = Column(Text)
    map_link = Column(Text)
    link = Column(String(255), unique=True)
    external_link = Column(String(255))
    listing_created_time = Column(TIMESTAMPTZ)
    listing_last_refresh_time = Column(TIMESTAMPTZ)
    price_per_m = Column(Numeric(6, 2))
    floor = Column(Integer)
    furniture = Column(String(3))
    market = Column(String(25))
    builttype = Column(String(50))
    surface = Column(Numeric(4, 2))
    rooms = Column(String(25))
    price = Column(Numeric(12, 2))
    currency = Column(String(3))
    negotiable = Column(Boolean)
    city = Column(String(50))
    district = Column(String(50))
    username = Column(String(255))
    is_business = Column(Boolean)
    images = Column(Text)
    image = Column(Text)



class OtodomListing(Base):
    __tablename__ = 'apartment_listings' #todo change

    id = Column(Integer, primary_key=True)

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
    platform = Column(String(50))
    date_last_seen = Column(DateTime)