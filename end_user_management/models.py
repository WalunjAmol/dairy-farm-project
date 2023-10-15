#Django Imports
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password

#Internal Imports
from dairy_management.models import Dairy
from admin_management.models import CustomUser


# Create your models here.

class EndUser(models.Model):
    dairy_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='end_users') 
    dairy_name = models.ForeignKey(Dairy, on_delete=models.CASCADE,related_name='dairy_customers')   
    custom_id = models.PositiveIntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    password = models.CharField(max_length=128, default=make_password("User@123"))
    birth_date = models.DateField(blank=True, null=True)
    mobile_number = models.CharField(
        unique=True,
        max_length=15
    )    
    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
        error_messages={
            "unique": "A user with that email already exists.",
        },
    )
    profile_photo = models.ImageField(upload_to='media/profile_photos/', blank=True, null=True)
    user_status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    password = models.CharField()

    def __str__(self):
        return f"{self.custom_id}-{self.first_name} {self.last_name}"