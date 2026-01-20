from django.shortcuts import render
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, ListCreateAPIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CategorySerializer, ProductSerializer
from .models import Category, Product
from rest_framework.permissions import IsAuthenticated , AllowAny



class CategoryListApiView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permissions_classes = [AllowAny]

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs)

category_list_api_view = CategoryListApiView.as_view()

class ProductListApiView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permissions_classes = [AllowAny]

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs)

product_list_api_view = ProductListApiView.as_view()


