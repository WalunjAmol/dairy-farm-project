from django.urls import path
from .views import MilkTransactionListView, MilkTransactionCreateView, MilkTransactionUpdateView, MilkTransactionDeleteView,import_transactions

app_name = 'milk_transaction'

urlpatterns = [
    path('milk_transactions/', MilkTransactionListView.as_view(), name='milk-transaction-list'),
    path('milk_transactions/create/', MilkTransactionCreateView.as_view(), name='milk-transaction-create'),
    path('milk_transactions/<int:pk>/update/', MilkTransactionUpdateView.as_view(), name='milk-transaction-update'),
    path('milk_transactions/<int:pk>/delete/', MilkTransactionDeleteView.as_view(), name='milk-transaction-delete'),
    path('import-transaction/', import_transactions, name='milk-transaction-import'),
]
