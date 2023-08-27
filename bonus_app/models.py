#Django Imports
from django.db import models
from django.utils import timezone

#Local Impoets
from end_user_management.models import EndUser

# Create your models here.

class Bonus(models.Model):
    user = models.ForeignKey(EndUser, on_delete=models.CASCADE, related_name='bonuses')
    bonus_date = models.DateField(default=timezone.now)
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user} - {self.bonus_date}"