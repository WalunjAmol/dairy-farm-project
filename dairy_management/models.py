from django.db import models
from django.utils import timezone

class Dairy(models.Model):
    name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=15, unique=True,blank=True,null=True)
    logo = models.ImageField(upload_to='media/dairy_logos/', blank=True, null=True)
    role = models.CharField(max_length=255, blank=True)
    
    # Location Fields
    street_address = models.CharField(max_length=255, blank=True,null=True)
    city = models.CharField(max_length=100, blank=True,null=True)
    state = models.CharField(max_length=100, blank=True,null=True)
    postal_code = models.CharField(max_length=20, blank=True,null=True)
    
    # Contact Information
    email = models.EmailField(blank=True,null=True)
    phone_number = models.CharField(max_length=20, blank=True)

    is_active = models.BooleanField(default=False, verbose_name="Active")
    is_deleted = models.BooleanField(default=False, verbose_name="Deleted")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Dairy Details
    date_established = models.DateField(blank=True, null=True)
    owner_name = models.CharField(max_length=255, blank=True)
    owner_contact = models.CharField(max_length=20, blank=True)
    milk_production_capacity = models.PositiveIntegerField(blank=True, null=True)
    products = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    operational_status = models.BooleanField(default=True)
    employee_count = models.PositiveIntegerField(blank=True, null=True)
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.role = self.name.replace(' ', '').lower()
        super().save(*args, **kwargs)

