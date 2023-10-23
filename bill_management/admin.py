from django.contrib import admin
from .models import GeneratedCycle

# Register your models here.
@admin.register(GeneratedCycle)
class GeneratedCycleAdmin(admin.ModelAdmin):
    pass

