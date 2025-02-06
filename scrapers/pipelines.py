from sqlalchemy import text
from shared.database import SessionLocal, init_db

class SQLAlchemyPipeline:
    def open_spider(self, spider):
        """Initialize DB when spider starts."""
        init_db()

    def process_item(self, item, spider):
        session = SessionLocal()
        try:
            stmt = text("""
                INSERT INTO apartment_listings (image, price, short_desc, address, rooms, surface, price_per_m, floor, seller, link, district, currency, platform, date_last_seen)
                VALUES (:image, :price, :short_desc, :address, :rooms, :surface, :price_per_m, :floor, :seller, :link, :district, :currency, :platform, CURRENT_TIMESTAMP)
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
                    district = EXCLUDED.district,
                    currency = EXCLUDED.currency,
                    platform = EXCLUDED.platform,
                    date_last_seen = CURRENT_TIMESTAMP
                RETURNING id, (xmax = 0) as is_insert
            """)

            result = session.execute(stmt, item)
            row = result.fetchone()

            if row.is_insert:
                spider.logger.info(f"New listing added: {item.get('link')}")
            else:
                spider.logger.info(f"Listing updated: {item.get('link')}")

            session.commit()

        except Exception as e:
            session.rollback()
            spider.logger.error(f"Failed to process item: {e}")
        finally:
            session.close()
        return item