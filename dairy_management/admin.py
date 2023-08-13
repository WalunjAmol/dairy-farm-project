from django.contrib import admin
from .models import Dairy

# Register your models here.
@admin.register(Dairy)
class DairyAdmin(admin.ModelAdmin):
    pass
