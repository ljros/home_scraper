import os
import requests
from datetime import datetime
import pytz
from sqlalchemy import text
from shared.database import SessionLocal

class MailgunReporter:
    def __init__(self):
        self.api_key = os.environ.get("MAILGUN_API_KEY")
        self.domain = os.environ.get("MAILGUN_DOMAIN")
        self.from_email = os.environ.get("FROM_EMAIL")
        self.to_email = os.environ.get("TO_EMAIL")
        self.session = SessionLocal()
        # Define timezone for consistent reporting
        self.timezone = pytz.timezone('Europe/Warsaw')  # Adjust to your local timezone

    def get_recent_listings(self, limit=50):
        """Retrieve the most recent real estate listings from the database"""
        try:
            # Query specifically for the olx_listings table with all its fields
            query = text("""
                SELECT id, platform, title, description, map_link, link, external_link, 
                       listing_created_time, listing_last_refresh_time, price_per_m, 
                       floor, furniture, market, builttype, surface, rooms, price,
                       currency, negotiable, city, district, username, is_business,
                       images, image, date_created, date_last_seen
                FROM olx_listings 
                ORDER BY date_created DESC 
                LIMIT :limit
            """)
            result = self.session.execute(query, {"limit": limit})
            
            # Convert to list of dictionaries
            listings = [dict(row._mapping) for row in result]
            return listings
                
        except Exception as e:
            print(f"Database error: {str(e)}")
            return []
    
    def format_listings_as_html(self, listings):
        """
        Format the real estate listings as an HTML table
        """
        if not listings:
            return "<p>No new listings available.</p>"
            
        # Build HTML table
        html = "<h2>Latest Real Estate Listings</h2>"
        html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        
        # Define the columns we want to display (not all of them)
        display_columns = [
            'title', 'price', 'currency', 'surface', 'price_per_m', 'rooms',
            'city', 'district', 'market', 'builttype', 'furniture', 
            'negotiable', 'date_created'
        ]
        
        # Table headers
        html += "<tr style='background-color: #f2f2f2;'>"
        for key in display_columns:
            html += f"<th style='padding: 8px; text-align: left;'>{key.replace('_', ' ').capitalize()}</th>"
        # Add a column for the link
        html += "<th style='padding: 8px; text-align: left;'>View Listing</th>"
        html += "</tr>"
        
        # Table rows
        for item in listings:
            html += "<tr>"
            for key in display_columns:
                value = item.get(key, '')
                
                # Format dates nicely
                if key in ['date_created', 'date_last_seen', 'listing_created_time', 'listing_last_refresh_time'] and value:
                    if isinstance(value, datetime):
                        value = value.strftime("%Y-%m-%d %H:%M")
                
                # Format boolean values
                if key == 'negotiable' and isinstance(value, bool):
                    value = "Yes" if value else "No"
                
                # Format furniture value if it's a code
                if key == 'furniture' and value:
                    furniture_types = {
                        1: "Yes",
                        0: "No"
                    }
                    value = furniture_types.get(value, value)
                
                # Format market type if it's a code
                if key == 'market' and value:
                    market_types = {
                        1: "Primary",
                        2: "Secondary"
                    }
                    value = market_types.get(value, value)
                
                html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{value}</td>"
            
            # Add the link to the original listing
            listing_url = item.get('link') or item.get('external_link') or '#'
            html += f"<td style='padding: 8px; border: 1px solid #ddd;'><a href='{listing_url}' target='_blank'>View</a></td>"
            
            html += "</tr>"
            
        html += "</table>"
        
        # Add some statistics
        html += self.generate_statistics(listings)
        
        return html
    
    def generate_statistics(self, listings):
        """Generate some basic statistics about the listings"""
        if not listings:
            return ""
        
        # Calculate average price and price per square meter
        prices = [item['price'] for item in listings if item.get('price')]
        price_per_m_values = [item['price_per_m'] for item in listings if item.get('price_per_m')]
        surfaces = [item['surface'] for item in listings if item.get('surface')]
        
        avg_price = sum(prices) / len(prices) if prices else 0
        avg_price_per_m = sum(price_per_m_values) / len(price_per_m_values) if price_per_m_values else 0
        avg_surface = sum(surfaces) / len(surfaces) if surfaces else 0
        
        # Count by city
        cities = {}
        for item in listings:
            city = item.get('city', 'Unknown')
            cities[city] = cities.get(city, 0) + 1
        
        # Create statistics HTML
        html = "<h2>Listing Statistics</h2>"
        html += "<div style='margin-bottom: 20px;'>"
        html += f"<p><strong>Total Listings:</strong> {len(listings)}</p>"
        html += f"<p><strong>Average Price:</strong> {avg_price:.2f}</p>"
        html += f"<p><strong>Average Price per m²:</strong> {avg_price_per_m:.2f}</p>"
        html += f"<p><strong>Average Surface:</strong> {avg_surface:.2f} m²</p>"
        
        # Top cities
        html += "<h3>Listings by City</h3>"
        html += "<ul>"
        for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:5]:  # Top 5 cities
            html += f"<li>{city}: {count} listings</li>"
        html += "</ul>"
        html += "</div>"
        
        return html
    
    def send_email(self, subject, html_content):
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
                "to": self.to_email,
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
        Generate and send daily report of real estate listings
        """
        try:
            # Get recent listings
            listings = self.get_recent_listings(limit=50)
            
            # Get current time in the specified timezone
            now = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
            
            # Create email content
            html_content = f"""
            <html>
            <body>
                <h1>Daily Real Estate Listings Report</h1>
                <p>Report generated on: {now}</p>
                
                <p>This email contains the latest real estate listings collected from OLX.</p>
                
                {self.format_listings_as_html(listings)}
                
                <hr>
                <p>This is an automated message from your real estate listing tracker.</p>
            </body>
            </html>
            """
            
            # Send the email
            subject = f"Real Estate Listings Daily Report - {datetime.now(self.timezone).strftime('%Y-%m-%d')}"
            return self.send_email(subject, html_content)
        
        except Exception as e:
            print(f"Error generating daily report: {str(e)}")
            return False