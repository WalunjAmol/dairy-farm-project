from django.contrib import admin
from .models import AdvancePayment  

# Register your models here.
@admin.register(AdvancePayment)
class AdvancePaymentAdmin(admin.ModelAdmin):
    pass
