from django.contrib import admin
from .models import Stock

# Register your models here.
# @admin.register(MasterModel)
# class MasterModelAdmin(admin.ModelAdmin):
#     pass

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    pass