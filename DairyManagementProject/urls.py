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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dairy-management/',include('dairy_owner_management.urls')),
    path('customer-management/',include('end_user_management.urls')),
    path('milk-transaction/',include('milk_transaction.urls')),
    path('bonus-management/',include('bonus_app.urls')),

    path('',HomeView.as_view(), name='dashboard'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
