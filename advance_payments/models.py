from django.db import models
from end_user_management.models import EndUser, Dairy
from django.utils import timezone

class AdvancePayment(models.Model):
    enduser = models.ForeignKey(EndUser, on_delete=models.CASCADE, related_name='advance_payments')
    dairy = models.ForeignKey(Dairy, on_delete=models.CASCADE, related_name='dairy_advance_payments')
    payment_date = models.DateField(default=timezone.now)
    payment_time = models.TimeField(default=timezone.now)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_used = models.BooleanField(default=False)  # BooleanField to indicate whether the advance payment has been used to deduct from bills (defaulted to False initially).
    used_date = models.DateField(blank=True, null=True)
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('deduct', 'deduct'),
            ('withdrawal', 'Withdrawal'),
        ],
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Advance Payment for {self.enduser} on {self.payment_date}"

    # You can uncomment and use the deduct_from_balance method if needed.
    # def deduct_from_balance(self, amount):
    #     if self.payment_amount >= amount:
    #         self.payment_amount -= amount
    #         self.save()
    #         return True
    #     return False
