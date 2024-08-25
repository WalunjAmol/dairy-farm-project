from django.urls import path
from .views import MilkTransactionListView, MilkTransactionCreateView, MilkTransactionUpdateView, MilkTransactionDeleteView,import_transactions,datatable_data, WorstUsersPerCycleView

app_name = 'milk_transaction'

urlpatterns = [
    path('milk_transactions/', MilkTransactionListView.as_view(), name='milk-transaction-list'),
    path('transaction_data/', datatable_data, name='transaction_data'),

    path('milk_transactions/create/', MilkTransactionCreateView.as_view(), name='milk-transaction-create'),
    path('milk_transactions/<int:pk>/update/', MilkTransactionUpdateView.as_view(), name='milk-transaction-update'),
    path('milk_transactions/<int:pk>/delete/', MilkTransactionDeleteView.as_view(), name='milk-transaction-delete'),
    path('import-transaction/', import_transactions, name='milk-transaction-import'),
    path('worst-users/', WorstUsersPerCycleView.as_view(), name='worst_users_per_cycle'),

]
