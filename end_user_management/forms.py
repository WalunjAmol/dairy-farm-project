#Python Imports
import re

#Django Imports
from django.core.exceptions import ValidationError
from django import forms

#Internal Imports
from .models import EndUser


class EndUserForm(forms.ModelForm):

    first_name = forms.CharField(
        label="First Name",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter First Name", "class": "form-control"}),
        error_messages={"required": "First name cannot be empty."},
    )
    
    last_name = forms.CharField(
        label="Last Name",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter Last Name", "class": "form-control"}),
        error_messages={"required": "Last name cannot be empty."},
    )
    
    custom_id = forms.IntegerField(
        label="Custom ID",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter Custom ID", "class": "form-control"}),
        error_messages={"required": "Custom ID cannot be empty."},
    )

    
    mobile_number = forms.CharField(
        label="Mobile Number",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter Mobile Number", "class": "form-control"}),
        error_messages={"required": "Mobile number cannot be empty."},
    )

    def __init__(self, *args, **kwargs):
        super(EndUserForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].label = "First Name"
        self.fields["last_name"].label = "Last Name"
        
        self.fields["first_name"].widget.attrs.update(
            {
                'class':'form-control',"placeholder": "Enter First Name",
            }
        )
        self.fields["last_name"].widget.attrs.update(
            {
                "placeholder": "Enter Last Name",
                'class':'form-control'
            }
        )
        self.fields["email"].widget.attrs.update(
            {
                "placeholder": "Enter Email Address",
                'class':'form-control'
            }
        )
        self.fields["mobile_number"].widget.attrs.update(
            {      
                "placeholder": "Enter Mobile Number",
                "class":"form-control"
            }
        )
        self.fields["custom_id"].widget.attrs.update(
            {
                'class':'form-control',"placeholder": "Enter Correct Cutsomer ID",
            }
        )
        self.fields["birth_date"].widget.attrs.update(
            {
                "placeholder": "Enter Date of Birth",
                'class':'form-control'
            }
        )
        self.fields["email"].widget.attrs.update(
            {
                "placeholder": "Enter Email Address",
                'class':'form-control'
            }
        )
 
    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        # Regular expression to match Indian mobile numbers (10 digits, starting with 7, 8, or 9)
        if not re.match(r'^[789]\d{9}$', mobile_number):
            raise ValidationError("Please enter a valid Indian mobile number.")
        return mobile_number
    
    class Meta:
        model = EndUser
        fields = [
            'custom_id',
            'first_name',
            'last_name',
            'birth_date',
            'mobile_number',
            'email',
            'profile_photo',
            'user_status',
            'is_deleted',
        ]
