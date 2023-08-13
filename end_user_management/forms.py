from django import forms
from .models import EndUser

class EndUserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EndUserForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].label = "First Name"
        self.fields["last_name"].label = "Last Name"
        # self.fields["password1"].label = "Password"
        # self.fields["password2"].label = "Confirm Password"
        # self.fields['gender'].widget = forms.CheckboxInput()
        
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
