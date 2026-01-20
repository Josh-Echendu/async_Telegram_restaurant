from django.urls import path
from .views import category_list_api_view, product_list_api_view


urlpatterns = [
    path('category/', category_list_api_view),
    path('products/', product_list_api_view),
]