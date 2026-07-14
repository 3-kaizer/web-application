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
                'name': 'Aurora Pro X1',
                'category': 'Over-Ear',
                'description': 'Experience pure audio bliss with the Aurora Pro X1. Featuring aerospace-grade aluminum construction, 50mm custom-tuned drivers, and advanced noise cancellation technology. The memory foam ear cushions provide ultimate comfort for extended listening sessions.',
                'specifications': 'Driver Size: 50mm\nFrequency Response: 4Hz - 40kHz\nImpedance: 32 Ohms\nWeight: 250g\nBattery Life: 30 hours\nNoise Cancellation: Active (ANC)\nConnectivity: Bluetooth 5.2, 3.5mm jack\nMaterials: Aluminum, Premium Leather',
                'price': 599.99,
                'stock': 15,
                'is_available': True,
            },
            {
                'name': 'Nebula Elite',
                'category': 'Wireless',
                'description': 'The Nebula Elite redefines wireless audio with its cutting-edge Bluetooth 5.3 technology and lossless audio codec support. Designed for the modern audiophile, these headphones deliver studio-quality sound with unprecedented wireless freedom.',
                'specifications': 'Driver Size: 40mm\nFrequency Response: 5Hz - 35kHz\nImpedance: 24 Ohms\nWeight: 240g\nBattery Life: 45 hours\nCodec Support: LDAC, aptX HD, AAC\nConnectivity: Bluetooth 5.3\nMaterials: Memory Foam, Protein Leather',
                'price': 749.99,
                'stock': 10,
                'is_available': True,
            },
            {
                'name': 'Cipher MK-II',
                'category': 'In-Ear',
                'description': 'Precision-engineered in-ear monitors that deliver concert-hall acoustics. The Cipher MK-II features dual dynamic drivers and a balanced armature for unparalleled detail retrieval. Crafted from medical-grade titanium for durability and comfort.',
                'specifications': 'Driver Configuration: 1DD + 1BA\nFrequency Response: 10Hz - 30kHz\nImpedance: 16 Ohms\nWeight: 8g (per earpiece)\nCable: Silver-plated OFC\nConnector: 3.5mm / USB-C\nMaterials: Titanium, Silicone\nNoise Isolation: -26dB',
                'price': 349.99,
                'stock': 25,
                'is_available': True,
            },
            {
                'name': 'Serenity Vintage',
                'category': 'On-Ear',
                'description': 'Timeless design meets modern audio technology. The Serenity Vintage pays homage to classic headphone aesthetics while incorporating premium 40mm neodymium drivers and advanced acoustic tuning. Perfect for those who appreciate vintage style with contemporary performance.',
                'specifications': 'Driver Size: 40mm Neodymium\nFrequency Response: 8Hz - 38kHz\nImpedance: 28 Ohms\nWeight: 195g\nBattery Life: 25 hours\nConnectivity: Bluetooth 5.0, 3.5mm\nMaterials: Genuine Leather, Steel\nStyle: Retro-Modern',
                'price': 449.99,
                'stock': 12,
                'is_available': True,
            },
        ]

        for product_data in products_data:
            category_name = product_data.pop('category')
            category = categories[category_name]
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    **product_data,
                    'category': category,
                    'slug': product_data['name'].lower().replace(' ', '-'),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Product already exists: {product.name}'))

        self.stdout.write(self.style.SUCCESS('Product population completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Total categories: {Category.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total products: {Product.objects.count()}'))