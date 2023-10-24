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


def deleteData(request):
    from_date = "2023-08-01"  # Use the 'YYYY-MM-DD' format for dates
    to_date = "2023-09-30"

    try:
        delete_data = MilkTransaction.objects.filter(date__range=(from_date, to_date))
        bonus_date = Bonus.objects.filter(bonus_date__range=(from_date, to_date))
        print('bonus_datebonus_datebonus_date',bonus_date)
        for data in delete_data:
            data.delete()  # Delete each data object
            print(f'Deleted data with date: {data.date}')

        for data in bonus_date:
            data.delete()  # Delete each data object
            print(f'Deleted data with date: {data.bonus_date}')
        return HttpResponse('Data deletion successful')  # Respond with a success message
    except Exception as e:
        print(f'Error deleting data: {str(e)}')
        return HttpResponse('Error deleting data')  # Respond with an error message


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

