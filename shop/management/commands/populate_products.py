from django.core.management.base import BaseCommand
from shop.models import Category, Product


class Command(BaseCommand):
    help = 'Populate the database with premium headphone listings'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting product population...'))

        # Create categories
        categories_data = [
            {'name': 'Over-Ear'},
            {'name': 'On-Ear'},
            {'name': 'In-Ear'},
            {'name': 'Wireless'},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'slug': cat_data['name'].lower().replace(' ', '-')}
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Create products
        products_data = [
            {
                'name': 'AudioVortex Aura Pro',
                'category': 'Over-Ear',
                'description': 'Experience pure audio bliss with the AudioVortex Aura Pro. Featuring aerospace-grade aluminum construction, 50mm custom-tuned drivers, and advanced noise cancellation technology. The memory foam ear cushions provide ultimate comfort for extended listening sessions.',
                'specifications': 'Battery Life: Up to 30 hours\nQuick Charge: 10 min for 6 hrs\nNoise Cancellation: Active ANC\nConnectivity: Bluetooth 5.2 + 3.5mm jack',
                'price': 499.99,
                'stock': 15,
                'is_available': True,
                'rating': 4.8,
                'review_count': 182000,
            },
            {
                'name': 'SonicPulse Nebula Elite',
                'category': 'Wireless',
                'description': 'The SonicPulse Nebula Elite redefines wireless audio with its cutting-edge Bluetooth 5.3 technology and lossless audio codec support. Designed for the modern audiophile, these headphones deliver studio-quality sound with unprecedented wireless freedom.',
                'specifications': 'Battery Life: Up to 45 hours\nCodec Support: LDAC, aptX HD\nConnectivity: Bluetooth 5.3',
                'price': 499.99,
                'stock': 10,
                'is_available': True,
                'rating': 4.9,
                'review_count': 214000,
            },
            {
                'name': 'BassPhantom Cipher Titanium',
                'category': 'In-Ear',
                'description': 'Precision-engineered in-ear monitors that deliver concert-hall acoustics. The BassPhantom Cipher Titanium features dual dynamic drivers and a balanced armature for unparalleled detail retrieval. Crafted from medical-grade titanium for durability and comfort.',
                'specifications': 'Driver Configuration: Dual drivers\nNoise Isolation: -26dB\nConnectivity: 3.5mm / USB-C',
                'price': 349.99,
                'stock': 25,
                'is_available': True,
                'rating': 4.6,
                'review_count': 97000,
            },
            {
                'name': 'RetroWave Serenity Classic',
                'category': 'On-Ear',
                'description': 'Timeless design meets modern audio technology. The RetroWave Serenity Classic pays homage to classic headphone aesthetics while incorporating premium 40mm neodymium drivers and advanced acoustic tuning. Perfect for those who appreciate vintage style with contemporary performance.',
                'specifications': 'Battery Life: Up to 25 hours\nStyle: Retro-modern design\nConnectivity: Bluetooth 5.0 + cable',
                'price': 449.99,
                'stock': 12,
                'is_available': True,
                'rating': 4.7,
                'review_count': 128000,
            },
            {
                'name': 'StudioBeats Pulse Pro',
                'category': 'Over-Ear',
                'description': 'Studio monitoring headphones tuned for a balanced, precise soundstage. StudioBeats Pulse Pro provides accurate mixing clarity with durable memory foam cups and refined noise isolation for long producing sessions.',
                'specifications': 'Driver Size: 45mm\nNoise Isolation: Passive\nConnectivity: 3.5mm wired',
                'price': 399.99,
                'stock': 18,
                'is_available': True,
                'rating': 4.5,
                'review_count': 86000,
            },
            {
                'name': 'Aurora Sound Echo One',
                'category': 'Over-Ear',
                'description': 'High-resolution audiophile headphones engineered for immersive listening. Aurora Sound Echo One delivers crisp highs, rich mids, and powerful lows with a luxurious fit and studio-grade sound reproduction.',
                'specifications': 'Driver Size: 50mm\nSound: Studio-grade clarity\nConnectivity: Wired',
                'price': 499.99,
                'stock': 14,
                'is_available': True,
                'rating': 4.9,
                'review_count': 156000,
            },
            {
                'name': 'BassForge Zero',
                'category': 'In-Ear',
                'description': 'Professional monitor earbuds built for punchy low end and crystalline detail. BassForge Zero offers a secure fit, rich bass response, and studio-ready transparency for performing artists and producers.',
                'specifications': 'Driver Configuration: Dual armature\nNoise Isolation: Passive\nConnectivity: 3.5mm',
                'price': 199.99,
                'stock': 30,
                'is_available': True,
                'rating': 4.4,
                'review_count': 74000,
            },
            {
                'name': 'ZenFlow Air',
                'category': 'Wireless',
                'description': 'Lightweight everyday wireless headphones with effortless comfort and responsive sound. ZenFlow Air blends long battery life with a soft, breathable fit for all-day listening in motion.',
                'specifications': 'Battery Life: Up to 32 hours\nConnectivity: Bluetooth 5.2\nCodec Support: AAC, SBC',
                'price': 299.99,
                'stock': 22,
                'is_available': True,
                'rating': 4.6,
                'review_count': 111000,
            },
        ]

        for product_data in products_data:
            category_name = product_data.pop('category')
            category = categories[category_name]
            
            defaults = {
                **product_data,
                'category': category,
                'slug': product_data['name'].lower().replace(' ', '-'),
            }
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=defaults,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
            else:
                for field_name, value in defaults.items():
                    setattr(product, field_name, value)
                product.save()
                self.stdout.write(self.style.WARNING(f'Updated product: {product.name}'))

        self.stdout.write(self.style.SUCCESS('Product population completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Total categories: {Category.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total products: {Product.objects.count()}'))