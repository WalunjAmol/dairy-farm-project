#Python Imports
import re

#Django Imports
from django.core.exceptions import ValidationError
from django import forms

#Internal Imports
from .models import AdvancePayment,EndUser

class AdvancePaymentForm(forms.ModelForm):

    def __init__(self,user, *args, **kwargs):
        super(AdvancePaymentForm, self).__init__(*args, **kwargs)
        self.fields['enduser'].queryset = EndUser.objects.filter(dairy_name__id=user.dairy.id)

        
        self.fields["enduser"].widget.attrs.update(
            {
                'class':'form-control',"placeholder": "Enter First Name",
            }
        )
        self.fields["payment_date"].widget.attrs.update(
            {
                "placeholder": "Enter Advance Payment Taken Date",
                'class':'form-control'
            }
        )
        self.fields["payment_time"].widget.attrs.update(
            {
                "placeholder": "Enter Advance Payment Taken Time",
                'class':'form-control'
            }
        )
        self.fields["payment_amount"].widget.attrs.update(
            {
                "placeholder": "Enter Advance Payment Amount",
                'class':'form-control'
            }
        )
        self.fields["description"].widget.attrs.update(
            {      
                "placeholder": "Enter Advance Payment Description",
                "class":"form-control"
            }
        )
        self.fields["transaction_type"].widget.attrs.update(
            {      
                "class":"form-control"
            }
        )
    
    class Meta:
        model = AdvancePayment
        fields = '__all__'
        # fields = [
        #     'user',
        #     'bonus_date',
        #     'bonus_amount',
        #     'description',
        #     'transaction_type',
        # ]
