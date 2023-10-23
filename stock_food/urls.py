# urls.py
from django.urls import path
from .views import *

app_name = 'stock_food_management'

urlpatterns = [
    path('stocks/', StockListView.as_view(), name='stock-list'),
    path('stocks/create/', StockCreateView.as_view(), name='stock-create'),
    path('stocks/<int:pk>/update/', StockUpdateView.as_view(), name='stock-update'),

    path('feedpurchase/create/', FeedPurchaseCreateView.as_view(), name='feedpurchase-create'),
    path('feedpurchase/', FeedPurchaseListView.as_view(), name='feedpurchase-list'),
    path('feedpurchase/<int:pk>/edit/', FeedPurchaseUpdateView.as_view(), name='feedpurchase-update'),
    path('feedpurchase/<int:pk>/delete/', FeedPurchaseDeleteView.as_view(), name='feedpurchase-delete'),
]
