# urls.py
from django.urls import path
from .views import *

app_name = 'bill_management'

urlpatterns = [
    path('generate-cycle/', ProcessAndStoreObjectsView.as_view(), name='generate_cycle'),
    path('user-bill-mgt/', BillMgtUserListView.as_view(), name='user-bill-mgt-list'),

    # Other URL patterns for your application...
]
