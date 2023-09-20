from django.contrib import admin
from .models import Bonus

# Register your models here.
@admin.register(Bonus)
class BonusAdmin(admin.ModelAdmin):
    pass
