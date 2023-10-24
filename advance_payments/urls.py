from django.urls import path
from .views import (
    AdvancePaymentEndUserListView,
    AdvancePaymentCreateView,
    get_total_withdrawal_amount,
    AdvancePaymentDetailViewView,
    AdvancePaymentUpdateView,
)

app_name = 'advance_payments'  # app name

urlpatterns = [
    path('advance-payment-users/', AdvancePaymentEndUserListView.as_view(), name='advance-payment-user-list'),
    path('create-advanced-payment/', AdvancePaymentCreateView.as_view(), name='advance-payyment-create'),
    path('update-advanced-payment/<int:pk>/', AdvancePaymentUpdateView.as_view(), name='advance-payyment-update'),
    path('get_total_withdrawal_amount/', get_total_withdrawal_amount, name='get_total_withdrawal_amount'),
    path('advance-payment-details/<int:pk>/', AdvancePaymentDetailViewView.as_view(), name='advance-payment-detail'),


    # path('bonuse-tansactions/', BonusListView.as_view(), name='bonus-list'),
    # path('bonuses/<int:pk>/', BonusDetailView.as_view(), name='bonus-detail'),
    # path('bonuses/<int:pk>/update/', BonusUpdateView.as_view(), name='bonus-update'),
    # path('bonuses/<int:pk>/delete/', BonusDeleteView.as_view(), name='bonus-delete'),
]
