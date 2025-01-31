
from flask import Blueprint, render_template

bp = Blueprint('apartments', __name__)

@bp.route('/')
def index():
    
    example_listings = [
        {
            'address': '123 Example Street',
            'price': '500,000',
            'rooms': '3',
            'surface': '75',
        },
        {
            'address': '456 Sample Road',
            'price': '750,000',
            'rooms': '4',
            'surface': '100',
        }
    ]

    return render_template('listings.html', listings=example_listings)