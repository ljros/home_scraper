import os
import random
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from datetime import datetime, timedelta
from email.email_reporter import MailgunReporter


SCRAPE_START_HOUR = int(os.getenv("SCRAPE_START_HOUR", 9))
SCRAPE_END_HOUR = int(os.getenv("SCRAPE_END_HOUR", 21))
SCRAPES_PER_DAY = int(os.getenv("SCRAPES_PER_DAY", 4))
SEND_REPORT_HOUR = int(os.getenv("SEND_REPORT_HOUR"))
TIMEZONE = pytz.timezone(os.getenv("TIMEZONE", "Europe/Paris"))

class DynamicScrapeScheduler:
    def __init__(self, spider_names):
        self.spider_names = spider_names
        self.reporter = MailgunReporter()
        self.daily_trigger_times = {}
    
    def generate_daily_trigger_times(self):
        total_scrape_hours = SCRAPE_END_HOUR - SCRAPE_START_HOUR
        interval_hours = total_scrape_hours / (SCRAPES_PER_DAY - 1)
        trigger_times = []

        for i in range(SCRAPES_PER_DAY):
            base_hour = SCRAPE_START_HOUR + (i * interval_hours)
            
            # Add significant randomness to hour placement
            hour_variation = random.uniform(-0.5, 0.5) * interval_hours
            varied_hour = base_hour + hour_variation
            
            varied_hour = max(SCRAPE_START_HOUR, min(SCRAPE_END_HOUR, varied_hour))
            
            random_minutes = random.randint(0, 59)
            random_seconds = random.randint(0, 59)
            
            trigger_time = datetime.now(TIMEZONE).replace(
                hour=int(varied_hour),
                minute=random_minutes,
                second=random_seconds,
                microsecond=0
            )
            
            trigger_times.append(trigger_time)
        
        return sorted(trigger_times)
    
    def run_spider(self, spider_name):
        try:
            current_time = datetime.now(TIMEZONE)
            print(f"Running {spider_name} spider at {current_time}")
            
            result = os.system(f"cd scrapers && scrapy crawl {spider_name}")
            
            if result == 0:
                print(f"Spider {spider_name} completed successfully at {current_time}")
            else:
                print(f"Spider {spider_name} encountered an error at {current_time}")
        except Exception as e:
            print(f"Exception occurred while running {spider_name}: {e}")
    
    def setup_daily_scheduler(self):
        scheduler = BlockingScheduler(timezone=TIMEZONE)
        
        self.daily_trigger_times = {
            spider: self.generate_daily_trigger_times() 
            for spider in self.spider_names
        }
        
        # spiders
        for spider, trigger_times in self.daily_trigger_times.items():
            for i, trigger_time in enumerate(trigger_times, 1):
                scheduler.add_job(
                    func=lambda s=spider: self.run_spider(s),
                    trigger=CronTrigger(
                        hour=trigger_time.hour, 
                        minute=trigger_time.minute, 
                        second=trigger_time.second,
                        timezone=TIMEZONE
                    ),
                    id=f"{spider}_daily_trigger_{i}",
                    replace_existing=True
                )
                print(f"Scheduled {spider} trigger {i} at {trigger_time.strftime('%I:%M:%S %p')}")
        
        # email
        if SEND_REPORT_HOUR:
            scheduler.add_job(
                func=self.send_daily_email_report,
                trigger=CronTrigger(hour=SEND_REPORT_HOUR, minute=0, second=0, timezone=TIMEZONE),
                id='daily_email_report',
                replace_existing=True
            )
            print(f"Scheduled daily email report at {SEND_REPORT_HOUR}:00:00")
        else:
            print("Daily email report disabled")

        scheduler.add_job(
            func=self.regenerate_daily_schedules,
            trigger=CronTrigger(hour=0, minute=0, second=0, timezone=TIMEZONE),
            id='daily_schedule_regeneration'
        )
        
        return scheduler
    
    def regenerate_daily_schedules(self):
        print("Regenerating daily scraping schedules")
        
        self.daily_trigger_times = {
            spider: self.generate_daily_trigger_times() 
            for spider in self.spider_names
        }
        
    def send_daily_email_report(self):
        """
        Generate and send daily email report
        """
        try:
            current_time = datetime.now(TIMEZONE)
            print(f"Generating daily email report at {current_time}")
            
            result = self.reporter.send_daily_report()
            
            if result:
                print(f"Daily email report sent successfully at {current_time}")
            else:
                print(f"Failed to send daily email report at {current_time}")
        except Exception as e:
            print(f"Exception occurred while sending daily email report: {e}")

def main():
    spider_names = ['olx', 'otodom']
    
    dynamic_scheduler = DynamicScrapeScheduler(spider_names)
    scheduler = dynamic_scheduler.setup_daily_scheduler()
    
    print(f"Dynamic Scrape Scheduler started at {datetime.now(TIMEZONE)}")
    
    try:
        scheduler.start()
    except (SystemExit):
        print("Scheduler stopped gracefully")

if __name__ == "__main__":
    main()