from flask import Blueprint, render_template
from ..shared.database import SessionLocal
from ..models import ApartmentListing

bp = Blueprint('apartments', __name__)

@bp.route('/')
def listings():
    session = SessionLocal()

    # Fetch query parameters for filtering
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    seller = request.args.get('seller')

    # Base query
    query = session.query(ApartmentListing)

    # Apply filters
    if min_price:
        query = query.filter(ApartmentListing.price >= min_price)
    if max_price:
        query = query.filter(ApartmentListing.price <= max_price)
    if seller:
        query = query.filter(ApartmentListing.seller.ilike(f"%{seller}%"))

    listings = query.all()
    session.close()
    # example_listings = [
    #     {
    #         'address': '123 Example Street',
    #         'price': '500,000',
    #         'rooms': '3',
    #         'surface': '75',
    #     },
    #     {
    #         'address': '456 Sample Road',
    #         'price': '750,000',
    #         'rooms': '4',
    #         'surface': '100',
    #     }
    # ]

    return render_template('listings_new.html', listings=listings)