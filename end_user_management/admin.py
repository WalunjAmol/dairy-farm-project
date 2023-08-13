from django.contrib import admin
from .models import EndUser

# Register your models here.
@admin.register(EndUser)
class EndUserAdmin(admin.ModelAdmin):
    pass
