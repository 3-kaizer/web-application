# Audio Lux

A polished Django storefront for premium headphones.

## Run locally

1. Create and activate a virtual environment.
2. Install the project requirements: `pip install django pillow`.
3. Run `python manage.py migrate`.
4. Optionally load the sample catalogue: `python manage.py populate_products`.
5. Start the app: `python manage.py runserver`.

The storefront is available at `http://127.0.0.1:8000/`.

## Included

- Responsive premium shop, product, bag, checkout, confirmation, and account screens
- Category filtering, cart quantities, guest carts, and account cart merging
- Functional checkout totals including 8% estimated tax
- Product and order management through Django admin

Do not use the development `SECRET_KEY`, `DEBUG=True`, or any sample credentials in a production deployment.
