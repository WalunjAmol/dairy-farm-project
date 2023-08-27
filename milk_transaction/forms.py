from django import forms
from .models import MilkTransaction

class MilkTransactionForm(forms.ModelForm):
    class Meta:
        model = MilkTransaction
        fields = '__all__'
        widgets = {
            'end_user': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'society_code': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'Enter Society Code'}),
            'center_code': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'Enter Center Code'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'Enter Type'}),
            'transaction_subtype': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'Enter Subtype'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'required': 'required', 'type': 'date', 'placeholder': 'Enter Date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'required': 'required', 'type': 'time', 'placeholder': 'Enter Time'}),
            'transaction_shift': forms.Select(attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'Enter Shift'}),
            'transaction_producer': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'Enter Customer ID'}),
            'transaction_liters': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'Enter Liters'}),
            'transaction_fat': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'Enter Fat'}),
            'transaction_snf': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'Enter SNF'}),
            'transaction_rate': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'Enter Rate'}),
            'transaction_off_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Off Amount'}),
            'transaction_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Total Amount'}),
            'transaction_subtype_2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Subtype 2'}),
        }
        error_messages = {
            'society_code': {'required': 'This field is required.'},
            'center_code': {'required': 'This field is required.'},
            'transaction_type': {'required': 'This field is required.'},
            'transaction_shift': {'required': 'This field is required.'},
            'transaction_producer': {'required': 'This field is required.'},
            'transaction_liters': {'required': 'This field is required.'},
            'transaction_fat': {'required': 'This field is required.'},
            'transaction_snf': {'required': 'This field is required.'},
            # Add other required fields and their error messages here...
        }
