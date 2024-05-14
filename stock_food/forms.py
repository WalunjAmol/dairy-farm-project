# forms.py
from django import forms
from .models import Stock,FeedPurchase

class StockForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].required = True
        # self.fields['original_price'].required = True
        # self.fields['selling_price'].required = True
        self.fields['marathit_name'].required = True
        self.fields['quantity'].required = True
        self.fields['marathit_name'].required = True

        # Update individual field widgets if needed
        self.fields['name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Feed Name (e.g., Premium Cow Feed)'})
        self.fields['original_price'].widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Original Price per Unit (e.g., 1000.00)'})
        self.fields['selling_price'].widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Selling Price per Unit (e.g., 1500.00)'})
        self.fields['quantity'].widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Available Quantity (e.g., 100)'})
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Feed Description (e.g., High-quality nutrition for dairy cows)'})
        self.fields["marathit_name"].widget.attrs.update(
                {      
                    "placeholder": "पशुखाद्याच नाव मराठीत टाका.",
                    "class":"form-control"
                }
            )
    class Meta:
        model = Stock
        fields = [ 'name', 'original_price', 'selling_price', 'quantity', 'description', 'marathit_name']
       

class StockUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].required = True
        # self.fields['original_price'].required = True
        # self.fields['selling_price'].required = True
        self.fields['quantity'].required = True
        self.fields['marathit_name'].required = True

        # Update individual field widgets if needed
        self.fields['name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Feed Name (e.g., Premium Cow Feed)'})
        self.fields['original_price'].widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Original Price per Unit (e.g., 1000.00)'})
        self.fields['selling_price'].widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Selling Price per Unit (e.g., 1500.00)'})
        self.fields['quantity'].widget = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Available Quantity (e.g., 100)'})
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Feed Description (e.g., High-quality nutrition for dairy cows)'})
        self.fields["marathit_name"].widget.attrs.update(
                {      
                    "placeholder": "पशुखाद्याच नाव मराठीत टाका.",
                    "class":"form-control"
                }
            )
    class Meta:
        model = Stock
        fields = ['name','original_price', 'selling_price', 'quantity', 'description', 'marathit_name']

class FeedPurchaseCreateForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['stock'].required = True
            self.fields['taken_user'].required = True
            self.fields['quantity_taken'].required = True
            self.fields['purchase_amount'].required = True

            self.fields["stock"].widget.attrs.update(
            {
                'class':'form-control',"placeholder": "Enter First Name",
            }
            )
            self.fields["taken_user"].widget.attrs.update(
                {
                    'class':'form-control'
                }
            )
            self.fields["quantity_taken"].widget.attrs.update(
                {
                    "placeholder": "'Enter Quantity Taken",
                    'class':'form-control'
                }
            )
            self.fields["purchase_amount"].widget.attrs.update(
                {      
                    "placeholder": "Enter Per Bag Amount",
                    "class":"form-control"
                }
            )
            self.fields["total_purchase_amount"].widget.attrs.update(
                {      
                    "placeholder": "Enter Total Amount",
                    "class":"form-control"
                }
            )
            
        class Meta:
            model = FeedPurchase
            fields = ['stock', 'taken_user', 'quantity_taken', 'purchase_amount','total_purchase_amount']

class FeedPurchaseUpdateForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # self.fields['stock'].required = True
            self.fields['taken_user'].required = True
            self.fields['quantity_taken'].required = True
            self.fields['purchase_amount'].required = True

            self.fields["stock"].widget.attrs.update(
            {
                'class':'form-control',"placeholder": "Enter First Name",
            }
            )
            self.fields["taken_user"].widget.attrs.update(
                {
                    'class':'form-control'
                }
            )
            self.fields["quantity_taken"].widget.attrs.update(
                {
                    "placeholder": "'Enter Quantity Taken",
                    'class':'form-control'
                }
            )
            self.fields["purchase_amount"].widget.attrs.update(
                {      
                    "placeholder": "Enter Per Bag Amount",
                    "class":"form-control"
                }
            )
            self.fields["total_purchase_amount"].widget.attrs.update(
                {      
                    "placeholder": "Enter Total Amount",
                    "class":"form-control"
                }
            )
            self.fields["description"].widget.attrs.update(
                {      
                    "placeholder": "Enter description",
                    "class":"form-control"
                }
            )
        class Meta:
            model = FeedPurchase
            fields = ['stock', 'taken_user', 'quantity_taken', 'purchase_amount','total_purchase_amount','is_paid','description']
    