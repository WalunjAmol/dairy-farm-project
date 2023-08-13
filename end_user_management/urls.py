from django.urls import path
from .views import (
    EndUserListView,
    EndUserCreateView,
    EndUserUpdateView,
    EndUserDeleteView,
)

app_name = 'end_user_management'  # app name

urlpatterns = [
    path('users/', EndUserListView.as_view(), name='user-list'),
    path('users/create/', EndUserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/update/', EndUserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/delete/', EndUserDeleteView.as_view(), name='user-delete'),
]
