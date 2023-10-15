# urls.py
from django.urls import path
from .views import *

app_name = 'stock_food_management'

urlpatterns = [
    path('stocks/', StockListView.as_view(), name='stock-list'),
    path('stocks/create/', StockCreateView.as_view(), name='stock-create'),
    path('stocks/<int:pk>/update/', StockUpdateView.as_view(), name='stock-update'),
    # Other URL patterns for your application...
]
