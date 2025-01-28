# pipelines.py

# Import SQLAlchemy components we'll need
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL

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
            # Create database item from scraped item
            db_item = ScrapedItem(
                image=item.get('image'),
                price=item.get('price'),
                short_desc=item.get('short_desc'),
                address=item.get('address'),
                rooms=item.get('rooms'),
                surface=item.get('surface'),
                price_per_m=item.get('price_per_m'),
                floor=item.get('floor'),
                seller=item.get('seller'),
                link=item.get('link')
            )
            session.add(db_item)
            session.commit()
        except Exception as e:
            # If anything goes wrong, rollback the session
            session.rollback()
            spider.logger.error(f"Failed to save item to database: {e}")
            raise
        finally:
            # Always close the session
            session.close()
        return item