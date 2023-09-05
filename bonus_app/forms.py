#Python Imports
import re

#Django Imports
from django.core.exceptions import ValidationError
from django import forms

#Internal Imports
from .models import Bonus,EndUser



class BonusForm(forms.ModelForm):

    def __init__(self,user, *args, **kwargs):
        super(BonusForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = EndUser.objects.filter(dairy_name__id=user.dairy.id)

        
        self.fields["user"].widget.attrs.update(
            {
                'class':'form-control',"placeholder": "Enter First Name",
            }
        )
        self.fields["bonus_date"].widget.attrs.update(
            {
                "placeholder": "Enter Bonus Taken Date",
                'class':'form-control'
            }
        )
        self.fields["bonus_amount"].widget.attrs.update(
            {
                "placeholder": "Enter Bonus Amount",
                'class':'form-control'
            }
        )
        self.fields["description"].widget.attrs.update(
            {      
                "placeholder": "Enter Bonus Description",
                "class":"form-control"
            }
        )
        self.fields["transaction_type"].widget.attrs.update(
            {      
                "class":"form-control"
            }
        )
    
    class Meta:
        model = Bonus
        fields = [
            'user',
            'bonus_date',
            'bonus_amount',
            'description',
            'transaction_type',
        ]
