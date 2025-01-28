from sqlalchemy.orm import sessionmaker
from .models import Base, ScrapedItem

class SQLAlchemyPipeline:
    def __init__(self, db_url):
        self.db_url = db_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_url=crawler.settings.get('DATABASE_URL')
        )

    def open_spider(self, spider):
        engine = create_engine(self.db_url)
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        session = self.Session()
        try:
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
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return item