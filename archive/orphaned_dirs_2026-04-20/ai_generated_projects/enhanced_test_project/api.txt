To build a REST API for a product catalog using Django REST Framework, you can follow the steps below:

1. Install Django and Django REST Framework:
```bash
pip install django djangorestframework
```

2. Create a new Django project and app:
```bash
django-admin startproject product_catalog_api
cd product_catalog_api
python manage.py startapp products
```

3. Define your models in the `products/models.py` file:
```python
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
```

4. Create serializers in the `products/serializers.py` file:
```python
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
```

5. Create viewsets in the `products/views.py` file:
```python
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def retrieve(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    def custom_action(self, request):
        # Implement your custom action logic here
        return Response({'message': 'Custom action executed'})
```

6. Define the URLs in the `products/urls.py` file:
```python
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = router.urls
```

7. Include the product URLs in the main `urls.py` file of your project:
```python
from django.urls import path, include

urlpatterns = [
    path('api/', include('products.urls')),
]
```

8. Run the Django development server and test your API:
```bash
python manage.py runserver
```

Your REST API for the product catalog is now ready to use with endpoints like `api/products/` for listing and creating products, `api/products/{id}/` for retrieving, updating, and deleting a specific product, and you can also define custom actions in the viewset as needed.