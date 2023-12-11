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
    marathi_name = forms.CharField(
        required=True,
        error_messages={"required": "Marathi name cannot be empty."},
    )

    bank_name = forms.CharField(
        required=True,
        error_messages={"required": "Bank name cannot be empty."},
    )

    account_number = forms.CharField(
        required=True,
        error_messages={"required": "Account number cannot be empty."},
    )

    confirm_account_number = forms.CharField(
        required=True,
        error_messages={"required": "Confirm Account number cannot be empty."},
    )
    ifsc_code = forms.CharField(
        required=True,
        error_messages={"required": "IFSC code cannot be empty."},
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
        self.fields["marathi_name"].widget.attrs.update(
                {      
                    "placeholder": "मराठीत नाव टाका.",
                    "class":"form-control"
                }
            )
        
        self.fields["bank_name"].widget.attrs.update(
            {
                "placeholder": "Enter Bank Name",
                'class': 'form-control'
            }
        )
        self.fields["account_number"].widget.attrs.update(
            {
                "placeholder": "Enter Account Number",
                'class': 'form-control'
            }
        )
        self.fields["confirm_account_number"].widget.attrs.update(
            {
                "placeholder": "Confirm Account Number",
                'class': 'form-control'
            }
        )
        self.fields["ifsc_code"].widget.attrs.update(
            {
                "placeholder": "Enter IFSC Code",
                'class': 'form-control'
            }
        )

 
    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        # Regular expression to match Indian mobile numbers (10 digits, starting with 7, 8, or 9)
        if not re.match(r'^[789]\d{9}$', mobile_number):
            raise ValidationError("Please enter a valid Indian mobile number.")
        return mobile_number

    def clean_confirm_account_number(self):
        cleaned_data = super().clean()
        account_number = cleaned_data.get("account_number")
        confirm_account_number = cleaned_data.get("confirm_account_number")

        # Check if the account numbers match

        # Check if the length of confirm_account_number is greater than the allowed maximum
        if confirm_account_number and len(confirm_account_number) > 254:
            raise forms.ValidationError("Confirm Account Number cannot exceed 254 characters.")

  
        if account_number and confirm_account_number and account_number != confirm_account_number:
            raise forms.ValidationError("Account numbers do not match.")

        return cleaned_data
    
    def clean_account_number(self):
        account_number = self.cleaned_data.get('account_number')

        # Check if the account number is exactly 10 digits (modify as needed)
        if account_number and not account_number.isdigit() or len(account_number) < 10:
            raise forms.ValidationError('Invalid account number. Please enter at least 10-digit number.')

        return account_number
    
    class Meta:
        model = EndUser
        fields = [
            'custom_id',
            'first_name',
            'last_name',
            'marathi_name',
            'birth_date',
            'mobile_number',
            'email',
            'profile_photo',
            'user_status',
            'is_deleted',
            'bank_name',
            'account_number',
            'confirm_account_number',
            'ifsc_code'
        ]
