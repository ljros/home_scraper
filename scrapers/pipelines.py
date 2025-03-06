from sqlalchemy import text
from shared.database import SessionLocal, init_db

class SQLAlchemyPipeline:
    def open_spider(self, spider):
        """Initialize DB when spider starts."""
        init_db()

    def process_item(self, item, spider):

        table_name = getattr(spider, 'table_name', 'apartment_listings')
        
        columns = item.keys()
        column_list = ", ".join(columns)
        placeholders = ", ".join([f":{col}" for col in columns])
        updates = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns])
        
        session = SessionLocal()        
        try:
            stmt = text(f"""
                INSERT INTO {table_name} ({column_list}, date_last_seen)
                VALUES ({placeholders}, CURRENT_TIMESTAMP)
                ON CONFLICT (link)
                DO UPDATE SET 
                    {updates},
                    date_last_seen = CURRENT_TIMESTAMP
                RETURNING id, (xmax = 0) as is_insert
            """)

            result = session.execute(stmt, item)
            row = result.fetchone()

            if row.is_insert:
                spider.logger.info(f"New {table_name} record added: {item.get('link')}")
            else:
                spider.logger.info(f"{table_name} record updated: {item.get('link')}")

            session.commit()

        except Exception as e:
            session.rollback()
            spider.logger.error(f"Failed to process item for {table_name}: {e}")
        finally:
            session.close()
        return item