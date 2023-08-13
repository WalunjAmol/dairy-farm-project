from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .manager import CustomUserManager
from dairy_management.models import Dairy

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
        error_messages={
            "unique": "A user with that email already exists.",
        },
    )
    mobile_number = models.CharField(
        unique=True,
        max_length=15
    )
    dairy = models.ForeignKey(Dairy, on_delete=models.SET_NULL, blank=True, null=True,related_name='users')
    birth_date = models.DateField(blank=True, null=True, help_text="Format: DD-MM-YYYY")
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='media/profile_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Active")
    is_deleted = models.BooleanField(default=False, verbose_name="Deleted")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile_number']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = "Custom User"
        verbose_name_plural = "Custom Users"

