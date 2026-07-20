from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from shop.models import Product
import os


class Command(BaseCommand):
    help = 'Link existing product images from media/products/ to product records'

    # Mapping of JPG filenames (without extension) to product slugs
    IMAGE_TO_SLUG = {
        'aura-pro': 'audiovortex-aura-pro',
        'nebula-elite': 'sonicpulse-nebula-elite',
        'cipher-titanium': 'bassphantom-cipher-titanium',
        'serenity-classic': 'retrowave-serenity-classic',
        'pulse-pro': 'studiobeats-pulse-pro',
        'echo-one': 'aurora-sound-echo-one',
        'bassforge-zero': 'bassforge-zero',
        'zenflow-air': 'zenflow-air',
    }

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Linking product images...'))

        media_products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        success_count = 0
        skip_count = 0
        not_found_count = 0

        for image_name, product_slug in self.IMAGE_TO_SLUG.items():
            jpg_path = os.path.join(media_products_dir, f'{image_name}.jpg')

            if not os.path.exists(jpg_path):
                self.stdout.write(self.style.WARNING(f'Image file not found: {jpg_path}'))
                not_found_count += 1
                continue

            try:
                product = Product.objects.get(slug=product_slug)
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Product not found for slug: {product_slug}'))
                not_found_count += 1
                continue

            # Skip if product already has an image
            if product.image:
                self.stdout.write(self.style.WARNING(f'Skipping {product.name} (already has image)'))
                skip_count += 1
                continue

            # Open the file and assign it to the product's image field
            with open(jpg_path, 'rb') as f:
                product.image.save(f'{image_name}.jpg', File(f), save=True)

            self.stdout.write(self.style.SUCCESS(f'✓ Linked {image_name}.jpg → {product.name}'))
            success_count += 1

        self.stdout.write(self.style.SUCCESS('\n=== Image Linking Complete ==='))
        self.stdout.write(self.style.SUCCESS(f'Successfully linked: {success_count}'))
        self.stdout.write(self.style.SUCCESS(f'Skipped (already has image): {skip_count}'))
        self.stdout.write(self.style.SUCCESS(f'Not found: {not_found_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total products: {Product.objects.count()}'))