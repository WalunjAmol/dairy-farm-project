from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


app_name = 'dairy_owner_management'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/',auth_views.LogoutView.as_view(next_page='/dairy-management/login/'),name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Add other URLs as needed
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    