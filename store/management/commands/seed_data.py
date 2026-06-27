from django.core.management.base import BaseCommand
from store.models import Category, Product
from django.utils.text import slugify


SAMPLE_DATA = [
    {
        'category': 'Electronics',
        'icon': 'fa-laptop',
        'products': [
            {
                'name': 'ProBook Ultra Laptop',
                'description': 'Powerful 15.6" laptop with Intel Core i7, 16GB RAM, 512GB SSD. Perfect for professionals and creators. Ultra-slim design with stunning IPS display.',
                'price': 1299.99,
                'sale_price': 999.99,
                'stock': 25,
                'featured': True,
            },
            {
                'name': 'NovaBuds Pro Wireless Earbuds',
                'description': 'Premium wireless earbuds with Active Noise Cancellation, 30-hour battery life, and crystal-clear sound. IPX5 water resistant.',
                'price': 199.99,
                'sale_price': 149.99,
                'stock': 80,
                'featured': True,
            },
            {
                'name': 'SmartWatch Series X',
                'description': 'Advanced smartwatch with health monitoring, GPS, AMOLED display, and 7-day battery. Compatible with iOS and Android.',
                'price': 349.99,
                'sale_price': None,
                'stock': 40,
                'featured': True,
            },
            {
                'name': '4K Action Camera',
                'description': 'Capture every adventure in stunning 4K at 60fps. Waterproof to 40m, includes mounting accessories and extra battery.',
                'price': 299.99,
                'sale_price': 249.99,
                'stock': 30,
                'featured': False,
            },
        ]
    },
    {
        'category': 'Fashion',
        'icon': 'fa-tshirt',
        'products': [
            {
                'name': 'Classic Slim-Fit Chinos',
                'description': 'Premium stretch chinos in a modern slim fit. Comfortable all-day wear with wrinkle-resistant fabric. Available in multiple colors.',
                'price': 89.99,
                'sale_price': 59.99,
                'stock': 120,
                'featured': True,
            },
            {
                'name': 'Leather Bifold Wallet',
                'description': 'Handcrafted genuine leather wallet with RFID blocking. Slim design holds 8 cards plus cash. Available in black and brown.',
                'price': 49.99,
                'sale_price': None,
                'stock': 200,
                'featured': False,
            },
            {
                'name': 'Running Performance Sneakers',
                'description': 'Lightweight, breathable running shoes with responsive foam cushioning. Perfect for daily runs and gym workouts.',
                'price': 129.99,
                'sale_price': 99.99,
                'stock': 75,
                'featured': True,
            },
            {
                'name': 'Casual Canvas Backpack',
                'description': '25L everyday backpack with laptop compartment, multiple pockets, and ergonomic straps. Water-resistant canvas material.',
                'price': 79.99,
                'sale_price': None,
                'stock': 60,
                'featured': False,
            },
        ]
    },
    {
        'category': 'Home & Living',
        'icon': 'fa-home',
        'products': [
            {
                'name': 'Smart LED Desk Lamp',
                'description': 'Adjustable color temperature and brightness. USB charging port, touch control, and eye-care technology. Modern minimalist design.',
                'price': 69.99,
                'sale_price': 49.99,
                'stock': 90,
                'featured': True,
            },
            {
                'name': 'Bamboo Cutting Board Set',
                'description': 'Set of 3 premium bamboo cutting boards in different sizes. Antimicrobial, durable, and eco-friendly. Easy to clean.',
                'price': 44.99,
                'sale_price': None,
                'stock': 150,
                'featured': False,
            },
            {
                'name': 'Aromatherapy Diffuser',
                'description': '500ml ultrasonic essential oil diffuser with 7-color LED lights, timer settings, and whisper-quiet operation.',
                'price': 39.99,
                'sale_price': 29.99,
                'stock': 110,
                'featured': False,
            },
        ]
    },
    {
        'category': 'Sports & Fitness',
        'icon': 'fa-dumbbell',
        'products': [
            {
                'name': 'Adjustable Dumbbell Set',
                'description': 'Space-saving adjustable dumbbells from 5 to 52.5 lbs. Quick-change weight system, durable construction. Replaces 15 sets of weights.',
                'price': 349.99,
                'sale_price': 299.99,
                'stock': 20,
                'featured': True,
            },
            {
                'name': 'Yoga Mat Premium',
                'description': 'Extra thick 6mm non-slip yoga mat with alignment lines. Eco-friendly TPE material, carrying strap included. 72" x 24".',
                'price': 59.99,
                'sale_price': None,
                'stock': 85,
                'featured': False,
            },
            {
                'name': 'Stainless Steel Water Bottle',
                'description': 'Double-walled 32oz insulated bottle. Keeps drinks cold 24hrs, hot 12hrs. BPA-free, leak-proof lid, wide mouth.',
                'price': 34.99,
                'sale_price': 24.99,
                'stock': 200,
                'featured': False,
            },
        ]
    },
    {
        'category': 'Books & Media',
        'icon': 'fa-book',
        'products': [
            {
                'name': 'Python for Data Science (Bundle)',
                'description': 'Complete 3-book bundle covering Python programming, machine learning, and data visualization. Perfect for beginners to advanced learners.',
                'price': 89.99,
                'sale_price': 59.99,
                'stock': 100,
                'featured': True,
            },
            {
                'name': 'E-Reader Paperwhite Edition',
                'description': '6" glare-free Paperwhite display, 32GB storage, weeks of battery life, and waterproof design. Carry your entire library anywhere.',
                'price': 249.99,
                'sale_price': 199.99,
                'stock': 45,
                'featured': True,
            },
        ]
    },
]


class Command(BaseCommand):
    help = 'Seed the database with sample products and categories'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding sample data...')
        created_count = 0

        for data in SAMPLE_DATA:
            cat, _ = Category.objects.get_or_create(
                name=data['category'],
                defaults={'icon': data['icon'], 'slug': slugify(data['category'])}
            )
            for p in data['products']:
                slug = slugify(p['name'])
                # Ensure unique slug
                if Product.objects.filter(slug=slug).exists():
                    self.stdout.write(f"  Skipping '{p['name']}' (already exists)")
                    continue
                Product.objects.create(
                    category=cat,
                    name=p['name'],
                    slug=slug,
                    description=p['description'],
                    price=p['price'],
                    sale_price=p.get('sale_price'),
                    stock=p['stock'],
                    featured=p.get('featured', False),
                    active=True,
                )
                created_count += 1
                self.stdout.write(f"  Created: {p['name']}")

        self.stdout.write(self.style.SUCCESS(f'\nDone! Created {created_count} products.'))
