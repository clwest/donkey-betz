# REST API
from rest_framework import viewsets, serializers
from .models import Product, Order

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        # Agent-enhanced creation logic
        product = serializer.save()
        # Trigger inventory management agent
        self.trigger_inventory_agent(product)
