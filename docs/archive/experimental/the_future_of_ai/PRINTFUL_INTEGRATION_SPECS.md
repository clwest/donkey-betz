# 🛍️ Phase 1: Print-on-Demand (Printful Integration) - Technical Specifications

**Date:** November 5, 2025
**Status:** 📋 Planning Phase
**Priority:** ⭐⭐⭐⭐⭐ HIGHEST
**Complexity:** 🟢 Low
**Time Estimate:** 3-5 days development, 2-3 days testing
**Revenue Potential:** $10-20 per sale, immediate

---

## 🎯 Overview

**Goal:** Enable users to turn AI-generated images into physical products (t-shirts, mugs, posters, etc.) with automatic order fulfillment through Printful.

**Why Printful:**
- ✅ No upfront costs or inventory
- ✅ 320+ products available
- ✅ Automatic fulfillment (they print & ship)
- ✅ Robust API with mockup generation
- ✅ Global shipping
- ✅ Quality guarantee

**User Journey:**
```
1. User creates AI image in Donkey Betz
2. User clicks "Create Product" button
3. User selects product type (t-shirt, mug, poster, etc.)
4. System generates product mockup with design
5. User customizes (size, color)
6. User orders → Printful fulfills → User receives product
```

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────┐
│      Donkey Betz Platform (Current)         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Generate │→ │ Upscale  │→ │  Gallery │  │
│  │  Image   │  │   4K     │  │   Save   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
                    ▼
        ┌───────────────────────┐
        │  NEW: Product Module  │
        └───────────────────────┘
                    ▼
        ┌───────────────────────┐
        │     Printful API      │
        │  - Catalog Sync       │
        │  - Mockup Generator   │
        │  - Order Creation     │
        │  - Webhook Handlers   │
        └───────────────────────┘
                    ▼
        ┌───────────────────────┐
        │  Printful Fulfillment │
        │  - Print Product      │
        │  - Package & Ship     │
        │  - Track Delivery     │
        └───────────────────────┘
```

### Data Flow

```
Image from Gallery
        ▼
┌──────────────────┐
│ Upload to CDN    │ (S3/CloudFront) - Your existing system
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Printful API:    │
│ Create Print File│ (4K, CMYK, proper DPI)
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Generate Mockup  │ (Product with design preview)
└────────┬─────────┘
         ▼
┌──────────────────┐
│ User Reviews &   │
│ Places Order     │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Create Order     │
│ in Printful      │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Printful Fulfills│ (2-7 days)
│ Ships to User    │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Delivery         │
│ Confirmation     │
└──────────────────┘
```

---

## 💾 Database Schema

### New Models

```python
# content/models.py

class PhysicalProduct(models.Model):
    """Base model for all physical products"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=50)  # 't-shirt', 'mug', 'poster'
    source_image = models.ForeignKey('ImageHistory', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, default='draft')
    # Status: 'draft', 'mockup_ready', 'ordered', 'processing', 'shipped', 'delivered'

    class Meta:
        db_table = 'physical_products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]


class PrintfulProduct(models.Model):
    """Print-on-demand products via Printful API"""
    product = models.OneToOneField(PhysicalProduct, on_delete=models.CASCADE, related_name='printful_data')

    # Printful catalog references
    printful_product_id = models.IntegerField()
    # Examples:
    # 71 = Bella Canvas 3001 Unisex T-Shirt
    # 19 = 11oz Ceramic Mug
    # 1 = Poster (various sizes)

    printful_variant_id = models.IntegerField()
    # Variant = size + color combination
    # Example: 4012 = Medium, Black for product 71

    # Product details (cached from Printful)
    product_name = models.CharField(max_length=200)
    variant_name = models.CharField(max_length=200)  # "Medium / Black"
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=50)
    color_code = models.CharField(max_length=20, null=True)  # Hex code

    # Design placement
    print_file_url = models.URLField()  # High-res design file
    placement = models.CharField(max_length=50, default='front')  # 'front', 'back', 'full'
    design_width = models.IntegerField()  # Width in pixels
    design_height = models.IntegerField()  # Height in pixels
    design_x_offset = models.IntegerField(default=0)  # X position
    design_y_offset = models.IntegerField(default=0)  # Y position

    # Mockup
    mockup_url = models.URLField(null=True, blank=True)
    mockup_generated_at = models.DateTimeField(null=True, blank=True)

    # Pricing (in USD)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price to customer
    printful_cost = models.DecimalField(max_digits=10, decimal_places=2)  # Printful's cost
    profit_margin = models.DecimalField(max_digits=10, decimal_places=2)  # Your profit

    # Order tracking
    printful_order_id = models.CharField(max_length=100, null=True, blank=True)
    order_status = models.CharField(max_length=50, null=True, blank=True)
    # Status: 'draft', 'pending', 'failed', 'canceled', 'onhold', 'inprocess', 'partial', 'fulfilled'

    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    tracking_url = models.URLField(null=True, blank=True)
    carrier = models.CharField(max_length=100, null=True, blank=True)

    shipped_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'printful_products'
        indexes = [
            models.Index(fields=['printful_order_id']),
            models.Index(fields=['order_status']),
        ]


class ProductOrder(models.Model):
    """Customer orders for physical products"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(PhysicalProduct)  # Support multiple items

    # Order metadata
    order_number = models.CharField(max_length=50, unique=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')
    # Status: 'pending', 'processing', 'shipped', 'delivered', 'canceled', 'refunded'

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Shipping information
    recipient_name = models.CharField(max_length=200)
    recipient_email = models.EmailField()
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state_code = models.CharField(max_length=20)  # State/Province
    zip_code = models.CharField(max_length=20)
    country_code = models.CharField(max_length=2)  # ISO 3166-1 alpha-2

    # Payment
    payment_method = models.CharField(max_length=50)  # 'stripe', 'paypal'
    payment_status = models.CharField(max_length=50, default='pending')
    # Status: 'pending', 'authorized', 'captured', 'failed', 'refunded'

    stripe_payment_intent_id = models.CharField(max_length=200, null=True, blank=True)
    stripe_charge_id = models.CharField(max_length=200, null=True, blank=True)

    # Fulfillment notes
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    class Meta:
        db_table = 'product_orders'
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['user', '-order_date']),
            models.Index(fields=['status']),
            models.Index(fields=['order_number']),
        ]

    def generate_order_number(self):
        """Generate unique order number: DB-YYYYMMDD-XXXX"""
        from django.utils import timezone
        date_str = timezone.now().strftime('%Y%m%d')
        random_suffix = ''.join(random.choices('0123456789', k=4))
        return f'DB-{date_str}-{random_suffix}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
```

### Migration Script

```python
# migrations/00XX_physical_products.py

from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('content', '00XX_previous_migration'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhysicalProduct',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('product_type', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default='draft', max_length=50)),
                ('source_image', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='content.imagehistory')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'physical_products',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PrintfulProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('printful_product_id', models.IntegerField()),
                ('printful_variant_id', models.IntegerField()),
                ('product_name', models.CharField(max_length=200)),
                ('variant_name', models.CharField(max_length=200)),
                ('size', models.CharField(max_length=20)),
                ('color', models.CharField(max_length=50)),
                ('color_code', models.CharField(max_length=20, null=True)),
                ('print_file_url', models.URLField()),
                ('placement', models.CharField(default='front', max_length=50)),
                ('design_width', models.IntegerField()),
                ('design_height', models.IntegerField()),
                ('design_x_offset', models.IntegerField(default=0)),
                ('design_y_offset', models.IntegerField(default=0)),
                ('mockup_url', models.URLField(blank=True, null=True)),
                ('mockup_generated_at', models.DateTimeField(blank=True, null=True)),
                ('retail_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('printful_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('profit_margin', models.DecimalField(decimal_places=2, max_digits=10)),
                ('printful_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('order_status', models.CharField(blank=True, max_length=50, null=True)),
                ('tracking_number', models.CharField(blank=True, max_length=100, null=True)),
                ('tracking_url', models.URLField(blank=True, null=True)),
                ('carrier', models.CharField(blank=True, max_length=100, null=True)),
                ('shipped_at', models.DateTimeField(blank=True, null=True)),
                ('estimated_delivery', models.DateField(blank=True, null=True)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='printful_data', to='content.physicalproduct')),
            ],
            options={
                'db_table': 'printful_products',
            },
        ),
        migrations.CreateModel(
            name='ProductOrder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('order_number', models.CharField(max_length=50, unique=True)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='pending', max_length=50)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('shipping_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('recipient_name', models.CharField(max_length=200)),
                ('recipient_email', models.EmailField()),
                ('address_line1', models.CharField(max_length=200)),
                ('address_line2', models.CharField(blank=True, max_length=200)),
                ('city', models.CharField(max_length=100)),
                ('state_code', models.CharField(max_length=20)),
                ('zip_code', models.CharField(max_length=20)),
                ('country_code', models.CharField(max_length=2)),
                ('payment_method', models.CharField(max_length=50)),
                ('payment_status', models.CharField(default='pending', max_length=50)),
                ('stripe_payment_intent_id', models.CharField(blank=True, max_length=200, null=True)),
                ('stripe_charge_id', models.CharField(blank=True, max_length=200, null=True)),
                ('customer_notes', models.TextField(blank=True)),
                ('admin_notes', models.TextField(blank=True)),
                ('products', models.ManyToManyField(to='content.physicalproduct')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'product_orders',
                'ordering': ['-order_date'],
            },
        ),
        migrations.AddIndex(
            model_name='physicalproduct',
            index=models.Index(fields=['user', '-created_at'], name='physical_pr_user_id_created_idx'),
        ),
        migrations.AddIndex(
            model_name='physicalproduct',
            index=models.Index(fields=['status'], name='physical_pr_status_idx'),
        ),
        migrations.AddIndex(
            model_name='printfulproduct',
            index=models.Index(fields=['printful_order_id'], name='printful_p_printfu_idx'),
        ),
        migrations.AddIndex(
            model_name='printfulproduct',
            index=models.Index(fields=['order_status'], name='printful_p_order_s_idx'),
        ),
        migrations.AddIndex(
            model_name='productorder',
            index=models.Index(fields=['user', '-order_date'], name='product_or_user_id_order_d_idx'),
        ),
        migrations.AddIndex(
            model_name='productorder',
            index=models.Index(fields=['status'], name='product_or_status_idx'),
        ),
        migrations.AddIndex(
            model_name='productorder',
            index=models.Index(fields=['order_number'], name='product_or_order_n_idx'),
        ),
    ]
```

---

## 🔧 Backend Implementation

### File Structure

```
content/
├── physical_products/
│   ├── __init__.py
│   ├── printful.py          # Main Printful API client
│   ├── products.py          # Product catalog management
│   ├── mockups.py           # Mockup generation
│   ├── orders.py            # Order creation & tracking
│   ├── webhooks.py          # Printful webhook handlers
│   └── pricing.py           # Pricing calculations
│
└── models.py (updated)      # Add PhysicalProduct models
```

### Printful API Client

```python
# content/physical_products/printful.py

import requests
from django.conf import settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PrintfulAPIClient:
    """Printful API client for print-on-demand operations"""

    BASE_URL = "https://api.printful.com"

    def __init__(self):
        self.api_key = settings.PRINTFUL_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Printful API"""
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Printful API error: {str(e)}")
            raise

    # ==================== CATALOG METHODS ====================

    def get_products(self) -> List[Dict]:
        """Get all available products from Printful catalog"""
        result = self._make_request("GET", "products")
        return result.get("result", [])

    def get_product_details(self, product_id: int) -> Dict:
        """Get detailed information about a specific product"""
        result = self._make_request("GET", f"products/{product_id}")
        return result.get("result", {})

    def get_variant_details(self, variant_id: int) -> Dict:
        """Get detailed information about a specific variant"""
        result = self._make_request("GET", f"products/variant/{variant_id}")
        return result.get("result", {})

    # ==================== MOCKUP METHODS ====================

    def create_mockup_task(self, variant_id: int, print_file_url: str, placement: str = "front") -> Dict:
        """
        Create a mockup generation task

        Args:
            variant_id: Printful variant ID
            print_file_url: URL to high-res design file
            placement: 'front', 'back', 'left', 'right', etc.

        Returns:
            Task ID for checking mockup status
        """
        data = {
            "variant_ids": [variant_id],
            "format": "jpg",
            "files": [
                {
                    "placement": placement,
                    "image_url": print_file_url,
                    "position": {
                        "area_width": 1800,
                        "area_height": 2400,
                        "width": 1800,
                        "height": 1800,
                        "top": 300,
                        "left": 0
                    }
                }
            ]
        }

        result = self._make_request("POST", "mockup-generator/create-task", data)
        return result.get("result", {})

    def get_mockup_task(self, task_key: str) -> Dict:
        """
        Check status of mockup generation task

        Returns:
            Status and mockup URLs when complete
        """
        result = self._make_request("GET", f"mockup-generator/task?task_key={task_key}")
        return result.get("result", {})

    # ==================== ORDER METHODS ====================

    def estimate_costs(self, recipient_country: str, items: List[Dict]) -> Dict:
        """
        Estimate costs for an order (shipping, tax, etc.)

        Args:
            recipient_country: 2-letter country code
            items: List of items with variant_id and quantity

        Returns:
            Cost breakdown including shipping and tax
        """
        data = {
            "recipient": {
                "country_code": recipient_country
            },
            "items": items
        }

        result = self._make_request("POST", "orders/estimate-costs", data)
        return result.get("result", {})

    def create_order(self, order_data: Dict, confirm: bool = False) -> Dict:
        """
        Create an order in Printful

        Args:
            order_data: Complete order data (recipient, items, etc.)
            confirm: If True, immediately confirms order and charges

        Returns:
            Order details including Printful order ID
        """
        endpoint = "orders" if not confirm else "orders?confirm=1"
        result = self._make_request("POST", endpoint, order_data)
        return result.get("result", {})

    def get_order(self, order_id: str) -> Dict:
        """Get order details"""
        result = self._make_request("GET", f"orders/{order_id}")
        return result.get("result", {})

    def confirm_order(self, order_id: str) -> Dict:
        """Confirm a draft order (triggers printing and shipping)"""
        result = self._make_request("POST", f"orders/{order_id}/confirm")
        return result.get("result", {})

    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order (only works if not yet fulfilled)"""
        result = self._make_request("DELETE", f"orders/{order_id}")
        return result.get("result", {})

    # ==================== SHIPPING METHODS ====================

    def get_shipping_rates(self, recipient_address: Dict, items: List[Dict]) -> List[Dict]:
        """Get available shipping options and rates"""
        data = {
            "recipient": recipient_address,
            "items": items
        }

        result = self._make_request("POST", "shipping/rates", data)
        return result.get("result", [])
```

### Product Catalog Manager

```python
# content/physical_products/products.py

from typing import Dict, List
from django.core.cache import cache
from .printful import PrintfulAPIClient
import logging

logger = logging.getLogger(__name__)

class ProductCatalogManager:
    """Manage Printful product catalog with caching"""

    CACHE_TIMEOUT = 86400  # 24 hours

    def __init__(self):
        self.client = PrintfulAPIClient()

    def get_featured_products(self) -> List[Dict]:
        """
        Get curated list of featured products for users

        Returns most popular products with simplified info
        """
        cache_key = "printful_featured_products"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Define featured products with good margins
        featured = [
            {
                "id": 71,
                "name": "Bella Canvas 3001 Unisex T-Shirt",
                "type": "t-shirt",
                "base_price": 12.95,
                "retail_price": 24.99,
                "profit": 12.04,
                "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
                "colors": ["Black", "White", "Navy", "Gray", "Red"],
                "popular": True
            },
            {
                "id": 19,
                "name": "11oz Ceramic Mug",
                "type": "mug",
                "base_price": 7.95,
                "retail_price": 14.99,
                "profit": 7.04,
                "sizes": ["11oz"],
                "colors": ["White"],
                "popular": True
            },
            {
                "id": 1,
                "name": "Poster",
                "type": "poster",
                "base_price": 8.99,
                "retail_price": 19.99,
                "profit": 11.00,
                "sizes": ["12×16", "18×24", "24×36"],
                "colors": ["N/A"],
                "popular": True
            },
            {
                "id": 14,
                "name": "Canvas Print",
                "type": "canvas",
                "base_price": 19.95,
                "retail_price": 49.99,
                "profit": 30.04,
                "sizes": ["12×16", "16×20", "18×24"],
                "colors": ["N/A"],
                "popular": False
            },
            {
                "id": 379,
                "name": "Unisex Hoodie",
                "type": "hoodie",
                "base_price": 29.50,
                "retail_price": 49.99,
                "profit": 20.49,
                "sizes": ["S", "M", "L", "XL", "2XL"],
                "colors": ["Black", "Navy", "Gray"],
                "popular": True
            },
            {
                "id": 307,
                "name": "Tote Bag",
                "type": "bag",
                "base_price": 12.95,
                "retail_price": 24.99,
                "profit": 12.04,
                "sizes": ["One Size"],
                "colors": ["Natural", "Black"],
                "popular": False
            },
        ]

        cache.set(cache_key, featured, self.CACHE_TIMEOUT)
        return featured

    def get_variants_for_product(self, product_id: int) -> List[Dict]:
        """
        Get all available variants (size/color combinations) for a product

        Returns variant IDs needed for ordering
        """
        cache_key = f"printful_product_variants_{product_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        product = self.client.get_product_details(product_id)
        variants = product.get("variants", [])

        cache.set(cache_key, variants, self.CACHE_TIMEOUT)
        return variants

    def get_variant_by_options(self, product_id: int, size: str, color: str) -> Optional[Dict]:
        """
        Find specific variant by size and color

        Example: get_variant_by_options(71, "M", "Black") → variant 4012
        """
        variants = self.get_variants_for_product(product_id)

        for variant in variants:
            if variant.get("size") == size and variant.get("color") == color:
                return variant

        return None

    def calculate_pricing(self, product_id: int, variant_id: int, markup_percentage: float = 100) -> Dict:
        """
        Calculate pricing with desired markup

        Args:
            product_id: Printful product ID
            variant_id: Printful variant ID
            markup_percentage: Markup percentage (100 = 2x, 50 = 1.5x)

        Returns:
            cost, retail_price, profit
        """
        variant = self.client.get_variant_details(variant_id)
        cost = float(variant.get("price", 0))

        retail_price = round(cost * (1 + markup_percentage / 100), 2)
        profit = round(retail_price - cost, 2)

        return {
            "cost": cost,
            "retail_price": retail_price,
            "profit": profit,
            "margin_percentage": round((profit / retail_price) * 100, 2)
        }
```

### Mockup Generator

```python
# content/physical_products/mockups.py

from typing import Dict
from .printful import PrintfulAPIClient
from django.core.files.storage import default_storage
from PIL import Image
import requests
import io
import time
import logging

logger = logging.getLogger(__name__)

class MockupGenerator:
    """Generate product mockups with user designs"""

    def __init__(self):
        self.client = PrintfulAPIClient()

    def generate_mockup(
        self,
        variant_id: int,
        design_url: str,
        placement: str = "front",
        max_wait_seconds: int = 60
    ) -> Dict:
        """
        Generate product mockup with design

        Args:
            variant_id: Printful variant ID
            design_url: URL to high-res design image
            placement: Where to place design ('front', 'back', etc.)
            max_wait_seconds: Max time to wait for mockup generation

        Returns:
            {
                'success': bool,
                'mockup_url': str,  # URL to generated mockup
                'task_key': str     # For checking status later
            }
        """
        try:
            # Step 1: Create mockup task
            logger.info(f"Creating mockup task for variant {variant_id}")
            task_result = self.client.create_mockup_task(
                variant_id=variant_id,
                print_file_url=design_url,
                placement=placement
            )

            task_key = task_result.get("task_key")
            if not task_key:
                return {"success": False, "error": "No task key returned"}

            # Step 2: Poll for completion
            logger.info(f"Polling mockup task {task_key}")
            start_time = time.time()

            while time.time() - start_time < max_wait_seconds:
                task_status = self.client.get_mockup_task(task_key)
                status = task_status.get("status")

                if status == "completed":
                    mockups = task_status.get("mockups", [])
                    if mockups:
                        mockup_url = mockups[0].get("mockup_url")
                        logger.info(f"Mockup generated: {mockup_url}")
                        return {
                            "success": True,
                            "mockup_url": mockup_url,
                            "task_key": task_key
                        }

                elif status == "failed":
                    error = task_status.get("error", {}).get("message", "Unknown error")
                    logger.error(f"Mockup generation failed: {error}")
                    return {"success": False, "error": error}

                # Still processing, wait before next check
                time.sleep(2)

            # Timeout
            logger.warning(f"Mockup generation timeout after {max_wait_seconds}s")
            return {
                "success": False,
                "error": "Timeout waiting for mockup generation",
                "task_key": task_key  # Can check later
            }

        except Exception as e:
            logger.error(f"Mockup generation error: {str(e)}")
            return {"success": False, "error": str(e)}

    def prepare_design_file(self, source_image_path: str, target_width: int = 4500) -> str:
        """
        Prepare design file for printing

        - Ensure high resolution (300 DPI for print)
        - Convert to RGB if needed
        - Upload to CDN

        Returns URL to prepared file
        """
        try:
            # Load image
            image = Image.open(source_image_path)

            # Convert to RGB if necessary (for transparent PNGs)
            if image.mode in ("RGBA", "LA", "P"):
                # Create white background
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "RGBA":
                    background.paste(image, mask=image.split()[3])  # Use alpha channel
                else:
                    background.paste(image)
                image = background

            # Resize to target width while maintaining aspect ratio
            if image.width < target_width:
                ratio = target_width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((target_width, new_height), Image.Resampling.LANCZOS)

            # Save high-quality version
            buffer = io.BytesIO()
            image.save(buffer, format="PNG", quality=95, dpi=(300, 300))
            buffer.seek(0)

            # Upload to storage
            filename = f"printful/designs/{uuid.uuid4()}.png"
            saved_path = default_storage.save(filename, buffer)
            design_url = default_storage.url(saved_path)

            logger.info(f"Design file prepared: {design_url}")
            return design_url

        except Exception as e:
            logger.error(f"Design file preparation error: {str(e)}")
            raise
```

(Continued in next message due to length...)
