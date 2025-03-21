import requests
from datetime import datetime
from shared.database import SessionLocal

class MailgunReporter:
    def __init__(self):
        self.api_key = os.environ.get("MAILGUN_API_KEY")
        self.domain = os.environ.get("MAILGUN_DOMAIN")
        self.from_email = os.environ.get("FROM_EMAIL", f"Scraper <mailgun@{MAILGUN_DOMAIN}>")
        self.to_email = os.environ.get("TO_EMAIL")
        self.session = SessionLocal()

    def get_recent_data(self, limit=50):
        """Retrieve the most recent data from the database"""
        try:
            # Modify this query to match your actual database schema
            query = text("SELECT * FROM items ORDER BY created_at DESC LIMIT :limit")
            result = self.session.execute(query, {"limit": limit})
            
            # Convert to list of dictionaries
            data = [dict(row._mapping) for row in result]
            return data
                
        except Exception as e:
            print(f"Database error: {str(e)}")
            return []
    
    def format_data_as_html(self, data):
        """
        Format the data as an HTML table
        """
        if not data:
            return "<p>No data available.</p>"
            
        # Build HTML table
        html = "<h2>Latest Scraped Data</h2>"
        html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        
        # Table headers
        html += "<tr style='background-color: #f2f2f2;'>"
        for key in data[0].keys():
            # Skip internal columns if needed
            if key in ['id', 'created_at', 'updated_at']:
                continue
            html += f"<th style='padding: 8px; text-align: left;'>{key.capitalize()}</th>"
        html += "</tr>"
        
        # Table rows
        for item in data:
            html += "<tr>"
            for key, value in item.items():
                # Skip internal columns
                if key in ['id', 'created_at', 'updated_at']:
                    continue
                html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{value}</td>"
            html += "</tr>"
            
        html += "</table>"
        return html
    
    def send_email(self, to_email, subject, html_content):
        """
        Send an email with the provided content using Mailgun API
        """
        if not self.api_key or not self.domain:
            print("Mailgun credentials not set in environment variables")
            return False
            
        try:
            # Mailgun API endpoint
            url = f"https://api.mailgun.net/v3/{self.domain}/messages"
            
            # Request data
            data = {
                "from": self.from_email,
                "to": to_email,
                "subject": subject,
                "html": html_content
            }
            
            # Send request
            response = requests.post(
                url,
                auth=("api", self.api_key),
                data=data
            )
            
            # Check response
            if response.status_code == 200:
                print("Email sent successfully via Mailgun")
                return True
            else:
                print(f"Failed to send email: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def send_daily_report(self):
        """
        Generate and send daily report
        """
        try:
            data = self.get_recent_data(limit=50)
            
            # Generate report date and time
            now = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
            
            # Create email content
            html_content = f"""
            <html>
            <body>
                <h1>Daily Scraper Report</h1>
                <p>Report generated on: {now}</p>
                
                <p>This email contains the latest data collected by the scraper.</p>
                
                {self.format_data_as_html(data)}
                
                <p>This is an automated message from your scraper application.</p>
            </body>
            </html>
            """
            
            # Send the email
            subject = f"Daily Scraper Report - {datetime.now(TIMEZONE).strftime('%Y-%m-%d')}"
            return self.send_email(TO_EMAIL, subject, html_content)
        
        except Exception as e:
            print(f"Error generating daily report: {str(e)}")
            return False