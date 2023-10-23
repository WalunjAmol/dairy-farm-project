from django.db import models
from django.utils import timezone
from end_user_management.models import Dairy,EndUser
from admin_management.models import CustomUser


class MasterModel(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True

class Stock(MasterModel):
    marathit_name = models.CharField(max_length=255,blank=True,null=True)
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

    def __str__(self):
        return f'{self.marathit_name}'
        # return f'{self.marathit_name}   :-( स्टॉक ला {self.quantity} पिशव्या शिल्लक)'


class FeedPurchase(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL, null=True, related_name='feed_purchases_stock')
    taken_user = models.ForeignKey(EndUser, on_delete=models.SET_NULL, null=True, related_name='feed_purchases_user')
    quantity_taken = models.PositiveBigIntegerField(blank=True, null=True)
    purchase_amount = models.PositiveBigIntegerField(blank=True, null=True)
    total_purchase_amount = models.PositiveBigIntegerField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='feed_purchases_created_by')
    dairy = models.ForeignKey(Dairy, on_delete=models.SET_NULL, null=True, related_name='feed_purchases_dairy')