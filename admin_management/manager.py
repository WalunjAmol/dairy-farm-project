from django.contrib.auth.models import BaseUserManager
from django.core.validators import RegexValidator


class CustomUserManager(BaseUserManager):
    in_app_migration = True
    def create_user(self, email, mobile_number, password=None, **extra_fields):
        # if not email:
        #     raise ValueError("The Email field must be set")
        if not mobile_number:
            raise ValueError("The Mobile Number field must be set")

        email = self.normalize_email(email)
        mobile_number_validator = RegexValidator(
            regex=r'^\+91[6-9]\d{9}$',  # Adjust the regex pattern as needed
            message="Enter a valid mobile number.",
        )
        mobile_number_validator(mobile_number)

        user = self.model(email=email, mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    

    def create_superuser(self, email, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, mobile_number, password, **extra_fields)

