from django.contrib import admin
from .models import MilkTransaction,ImportTransaction

# Register your models here.
@admin.register(MilkTransaction)
class MilkTransactionAdmin(admin.ModelAdmin):
    pass

@admin.register(ImportTransaction)
class ImportTransactionAdmin(admin.ModelAdmin):
    pass
