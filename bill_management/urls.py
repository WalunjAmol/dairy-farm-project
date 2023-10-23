# urls.py
from django.urls import path
from .views import *

app_name = 'bill_management'

urlpatterns = [
    path('generate-cycle/', ProcessAndStoreObjectsView.as_view(), name='generate_cycle'),
    path('user-bill-mgt/<int:pk>', BillMgtUserListView.as_view(), name='user-bill-mgt-list'),
    path('generate-bill/<int:user_id>/<int:cycle_id>',GenerateBill.as_view(),name='generate_bills'),
    path('deduct_amount/', deduct_amount_view, name='deduct_amount'),


    # Other URL patterns for your application...
]
