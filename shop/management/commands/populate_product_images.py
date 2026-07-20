from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from shop.models import Product
from PIL import Image
from io import BytesIO
import os


class Command(BaseCommand):
    help = 'Generate and assign product placeholder images based on category'

    def get_image_for_category(self, category_name):
        """Generate a placeholder image using PIL"""
        try:
            img = Image.new('RGB', (800, 800), color='#121722')
            
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Draw a gradient background effect
            for y in range(800):
                r = int(18 + (y / 800) * 15)
                g = int(23 + (y / 800) * 12)
                b = int(34 + (y / 800) * 10)
                draw.line([(0, y), (800, y)], fill=(r, g, b))
            
            # Draw accent circle
            draw.ellipse([250, 250, 550, 550], outline='#c8ff3d', width=8)
            draw.ellipse([270, 270, 530, 530], outline='#c8ff3d', width=3)
            
            # Draw headphone icon (simplified)
            draw.arc([300, 280, 500, 420], start=0, end=180, fill='#c8ff3d', width=12)
            draw.rectangle([290, 380, 330, 440], fill='#c8ff3d')
            draw.rectangle([470, 380, 510, 440], fill='#c8ff3d')
            
            # Save to BytesIO
            output = BytesIO()
            img.save(output, format='JPEG', quality=90, optimize=True)
            output.seek(0)
            return output.read()
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Failed to create placeholder for {category_name}: {e}'))
            return None

    def process_image(self, image_data):
        """Process image: resize to square and optimize"""
        try:
            img = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Get dimensions
            width, height = img.size
            
            # Crop to square (center focus)
            min_dim = min(width, height)
            left = (width - min_dim) // 2
            top = (height - min_dim) // 2
            right = left + min_dim
            bottom = top + min_dim
            
            img = img.crop((left, top, right, bottom))
            
            # Resize to 800x800
            img = img.resize((800, 800), Image.Resampling.LANCZOS)
            
            # Save to BytesIO
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return output
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Image processing failed: {e}'))
            return None

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting product image population...'))

        # Ensure media directory exists
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'products'), exist_ok=True)

        products = Product.objects.all()
        success_count = 0
        skip_count = 0

        for product in products:
            # Skip if product already has an image
            if product.image:
                self.stdout.write(self.style.WARNING(f'Skipping {product.name} (already has image)'))
                skip_count += 1
                continue

            category_name = product.category.name
            self.stdout.write(f'Processing {product.name} ({category_name})...')

            # Download image
            image_data = self.get_image_for_category(category_name)
            if not image_data:
                self.stdout.write(self.style.WARNING(f'No image downloaded for {product.name}'))
                continue

            # Process image
            processed_image = self.process_image(image_data)
            if not processed_image:
                continue

            # Save image to product with premium naming
            filename = f"audiolux-{product.slug}.jpg"
            product.image.save(filename, ContentFile(processed_image.read()), save=True)
            
            self.stdout.write(self.style.SUCCESS(f'✓ Added image for {product.name}'))
            success_count += 1

        self.stdout.write(self.style.SUCCESS('\n=== Image Population Complete ==='))
        self.stdout.write(self.style.SUCCESS(f'Successfully added images: {success_count}'))
        self.stdout.write(self.style.SUCCESS(f'Skipped (already exists): {skip_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total products: {products.count()}'))