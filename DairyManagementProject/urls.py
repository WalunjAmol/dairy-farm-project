"""
URL configuration for DairyManagementProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from dairy_owner_management.views import HomeView
from milk_transaction.models import MilkTransaction
from django.http import HttpResponse  # Import HttpResponse
from bonus_app.models import Bonus
from pprint import pprint
from django.http import HttpResponse
from datetime import date

def deleteData(request):

    # Define the start and end dates for filtering
    start_date = date(2024, 1, 16)  # Replace with your start date
    end_date = date(2024, 2, 10)  # Replace with your end date

    # Filter MilkTransaction records between dates
    milk_transactions = MilkTransaction.objects.filter(date__range=(start_date, end_date))

    # Filter Bonus records between dates
    bonuses = Bonus.objects.filter(bonus_date__range=(start_date, end_date))

    # Compare Bonus foreign key IDs with MilkTransaction object IDs
    for bonus in bonuses:
        milk_transaction_id = bonus.milk_transaction_id

        # Get the list of MilkTransaction IDs within the date range
        milk_transaction_ids_within_range = milk_transactions.values_list('id', flat=True)

        if milk_transaction_id not in milk_transaction_ids_within_range:
            # If MilkTransaction object is not present, delete the Bonus record
            bonus.delete()
            print(f"Deleted Bonus record with ID {bonus}")

    return HttpResponse('test')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('dairy-management/',include('dairy_owner_management.urls')),
    path('customer-management/',include('end_user_management.urls')),
    path('milk-transaction/',include('milk_transaction.urls')),
    path('bonus-management/',include('bonus_app.urls')),
    path('advance-payment-mgt/',include('advance_payments.urls')),
    path('',HomeView.as_view(), name='dashboard'),
    path('stock/',include('stock_food.urls')),
    path('bill-mgt/',include('bill_management.urls')),
    path('delete/', deleteData, name='delete_data'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

