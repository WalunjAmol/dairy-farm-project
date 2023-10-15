from django.db import models
from django.utils import timezone

from dairy_management.models import Dairy
from admin_management.models import CustomUser

class GeneratedCycle(models.Model):
    name = models.CharField(max_length=100)
    dairy_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='generated_cycles_dairy_owner') 
    dairy_name = models.ForeignKey(Dairy, on_delete=models.CASCADE, null=True, related_name='generated_cycles_dairy_name')  
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
