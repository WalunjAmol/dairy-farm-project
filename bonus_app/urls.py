from django.urls import path
from .views import (
    BonusListView, 
    BonusDetailView, 
    BonusCreateView, 
    BonusUpdateView, 
    BonusDeleteView,
    BonusEndUserListView,
    user_bonuses,
    update_bonus_status,
    all_user_bonuses,
)

app_name = 'bonus'  # app name

urlpatterns = [
    path('bonus-users/', BonusEndUserListView.as_view(), name='bonus-user-list'),
    path('bonuse-tansactions/', BonusListView.as_view(), name='bonus-list'),
    path('bonuses/<int:pk>/', BonusDetailView.as_view(), name='bonus-detail'),
    path('bonuses/create/', BonusCreateView.as_view(), name='bonus-create'),
    path('bonuses/<int:pk>/update/', BonusUpdateView.as_view(), name='bonus-update'),
    path('bonuses/<int:pk>/delete/', BonusDeleteView.as_view(), name='bonus-delete'),
    path('bonuses/user/<int:user_id>/', user_bonuses, name='user_bonuses'),
    path('bonuses/update-bonus-status/', update_bonus_status, name='update_bonus_status'),
    path('bonuses/', all_user_bonuses, name='all_user_bonuses'),


]
