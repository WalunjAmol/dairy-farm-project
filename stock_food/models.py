from django.db import models
from django.utils import timezone
from end_user_management.models import Dairy
from admin_management.models import CustomUser


class MasterModel(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.symbol} - {self.name}'


class Stock(MasterModel):
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_added = models.DateField(auto_now_add=True)
    date_created = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='stocks_created')
    dairy = models.ForeignKey(Dairy, on_delete=models.SET_NULL, null=True, related_name='stocks')
