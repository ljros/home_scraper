# pipelines.py

# Import SQLAlchemy components we'll need
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy import text


# Import our database models
from .models import Base, ScrapedItem

class SQLAlchemyPipeline:
    def __init__(self, db_url):
        """Initialize the pipeline with database URL."""
        self.db_url = db_url
        self.Session = None

    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance with database URL from settings."""
        # Get DATABASE_URL from Scrapy settings (which gets it from environment)
        return cls(
            db_url=crawler.settings.get('DATABASE_URL')
        )

    def open_spider(self, spider):
        """When spider opens, create database engine and tables."""
        # Create database engine
        engine = create_engine(self.db_url)
        # Create all tables defined in models.py
        Base.metadata.create_all(engine)
        # Create session factory
        self.Session = sessionmaker(bind=engine)

    def close_spider(self, spider):
        """Clean up when spider closes."""
        pass

    def process_item(self, item, spider):
        """Save each scraped item to database."""
        session = self.Session()
        try:
            # # Create database item from scraped item
            # db_item = ScrapedItem(
            #     image=item.get('image'),
            #     price=item.get('price'),
            #     short_desc=item.get('short_desc'),
            #     address=item.get('address'),
            #     rooms=item.get('rooms'),
            #     surface=item.get('surface'),
            #     price_per_m=item.get('price_per_m'),
            #     floor=item.get('floor'),
            #     seller=item.get('seller'),
            #     link=item.get('link')
            # )
            # session.add(db_item)

            # Using raw SQL through SQLAlchemy to avoid duplicate entries
            stmt = text("""
                INSERT INTO scraped_items (image, price, short_desc, address, rooms, surface, price_per_m, floor, seller, link)
                VALUES (:image, :price, :short_desc, :address, :rooms, :surface, :price_per_m, :floor, :seller, :link)
                ON CONFLICT (link) 
                DO UPDATE SET 
                    image = EXCLUDED.image,
                    price = EXCLUDED.price,
                    short_desc = EXCLUDED.short_desc,
                    address = EXCLUDED.address,
                    rooms = EXCLUDED.rooms,
                    surface = EXCLUDED.surface,
                    price_per_m = EXCLUDED.price_per_m,
                    floor = EXCLUDED.floor,
                    seller = EXCLUDED.seller,
                    link = EXCLUDED.link,
                    date_last_seen = CURRENT_TIMESTAMP
                RETURNING id, (xmax = 0) as is_insert
            """)
            
            result = session.execute(
                stmt,
                {
                    'image': item.get('image'),
                    'price': item.get('price'),
                    'short_desc': item.get('short_desc'),
                    'address': item.get('address'),
                    'rooms': item.get('rooms'),
                    'surface': item.get('surface'),
                    'price_per_m': item.get('price_per_m'),
                    'floor': item.get('floor'),
                    'seller': item.get('seller'),
                    'link': item.get('link')
                }
            )
            row = result.fetchone()
            
            # Log whether this was an insert or update
            if row.is_insert:
                spider.logger.info(f"New listing added: {item.get('link')}")
            else:
                spider.logger.info(f"Listing updated: {item.get('link')}")
            
            session.commit()
            
        except Exception as e:
            # If anything goes wrong, rollback the session
            session.rollback()
            spider.logger.error(f"Failed to process item: {e}")
            raise
        finally:
            # Always close the session
            session.close()
        return item