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

    path('feedpurchase/user-wise-list/',UserWiseFeedPurchaseList.as_view(), name='user-wise-feed-purchase'),
    path('feedpurchase/user-feed-details/<int:pk>/',UserWiseFeedDetails.as_view(), name='user-wise-feed-purchase-details'),
    path('user-feedpurchase/<int:pk>/create/', UserFeedPurchaseCreateView.as_view(), name='user-feedpurchase-create'),
    path('user-feedpurchase/<int:pk>/edit/', UserFeedPurchaseUpdateView.as_view(), name='user-feedpurchase-update'),



]
