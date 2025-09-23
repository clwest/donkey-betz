from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Category

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured = self.queryset.filter(featured=True)[:10]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_to_cart(self, request, pk=None):
        product = self.get_object()
        quantity = request.data.get('quantity', 1)
        # Cart logic here
        return Response({'status': 'added to cart'})
