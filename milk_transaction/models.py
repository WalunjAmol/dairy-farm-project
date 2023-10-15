from django.db import models
from end_user_management.models import EndUser,Dairy
from django.utils.translation import gettext_lazy as _  # Import _ for translation

# Use Enums or Constants for transaction_type
class TransactionType(models.TextChoices):
    RECEIPT = 'R', _('Receipt')
    PAYMENT = 'P', _('Payment')

# Use Enums or Constants for transaction_shift
class TransactionShift(models.TextChoices):
    MORNING = 'M', _('Morning')
    EVENING = 'E', _('Evening')

class ImportTransaction(models.Model):
    dairy = models.ForeignKey(Dairy, on_delete=models.CASCADE, related_name='import_transactions',default=None)
    imported_transaction_name = models.CharField(max_length=255,blank=True,null= True)
    success_records = models.PositiveIntegerField(default=0)  # Default value for success_records
    success_csv = models.FileField(upload_to='media/imported_csv/success/')
    failed_records = models.PositiveIntegerField(default=0)  # Default value for failed_records
    failed_csv = models.FileField(upload_to='media/imported_csv/failed/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.imported_transaction_name


class MilkTransaction(models.Model):
    dairy = models.ForeignKey(Dairy, on_delete=models.CASCADE, related_name='dairy_milk_transactions',default=None)
    # import_transaction_id = models.ForeignKey(ImportTransaction,on_delete=models.CASCADE,blank=True,null=True)
    end_user = models.ForeignKey(EndUser, on_delete=models.CASCADE, related_name='milk_transactions')
    society_code = models.CharField(max_length=10,blank=True,null=True)
    center_code = models.CharField(max_length=10,blank=True,null=True)
    transaction_type = models.CharField(
        max_length=1, choices=TransactionType.choices,blank=True,null=True
    )     
    transaction_subtype = models.IntegerField(blank=True,null=True)
    date = models.DateField()
    time = models.TimeField()
    transaction_shift = models.CharField(
        max_length=1, choices=TransactionShift.choices,
    ) 
    transaction_producer = models.CharField(max_length=10)
    transaction_liters = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_fat = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_lacto = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    transaction_snf = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_water = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    transaction_protein = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    transaction_ph = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    transaction_rate = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    transaction_off_amount = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_subtype_2 = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.transaction_producer}-{self.end_user.first_name} {self.end_user.last_name}"
    
    def get_month_name(self):
        return self.date.strftime('%B')

