# forms.py
from django import forms
from .models import Stock

class StockForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].required = True
        self.fields['original_price'].required = True
        self.fields['selling_price'].required = True
        self.fields['quantity'].required = True
        # self.fields['description'].required = True

        # Update individual field widgets if needed
        self.fields['name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Feed Name (e.g., Premium Cow Feed)'})
        self.fields['original_price'].widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Original Price per Unit (e.g., 1000.00)'})
        self.fields['selling_price'].widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Selling Price per Unit (e.g., 1500.00)'})
        self.fields['quantity'].widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Available Quantity (e.g., 100)'})
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Feed Description (e.g., High-quality nutrition for dairy cows)'})

    class Meta:
        model = Stock
        fields = [ 'name', 'original_price', 'selling_price', 'quantity', 'description',]
       

class StockUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].required = True
        self.fields['original_price'].required = True
        self.fields['selling_price'].required = True
        self.fields['quantity'].required = True
        # self.fields['description'].required = True

        # Update individual field widgets if needed
        self.fields['name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Feed Name (e.g., Premium Cow Feed)'})
        self.fields['original_price'].widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Original Price per Unit (e.g., 1000.00)'})
        self.fields['selling_price'].widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Selling Price per Unit (e.g., 1500.00)'})
        self.fields['quantity'].widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Available Quantity (e.g., 100)'})
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Feed Description (e.g., High-quality nutrition for dairy cows)'})

    class Meta:
        model = Stock
        fields = ['name','original_price', 'selling_price', 'quantity', 'description']
