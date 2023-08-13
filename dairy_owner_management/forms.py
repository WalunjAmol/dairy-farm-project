from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import  gettext_lazy as _
from admin_management.models import CustomUser

class CustomLoginForm(forms.Form):
    email = forms.EmailField(label=_('Email'))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.fields["email"].widget.attrs.update({"placeholder": _("Enter Email Address")})
        self.fields["password"].widget.attrs.update({"placeholder": _("Enter Password")})

    def clean(self, *args, **kwargs):
        print('clened data',self.cleaned_data)
        email = self.cleaned_data.get("email").lower()
        password = self.cleaned_data.get("password")
        if not CustomUser.objects.filter(email=email):
            raise forms.ValidationError(_("User does not exists"))
        if email and password:
            self.user = authenticate(email=email, password=password)
            if self.user is None:
                raise forms.ValidationError(_("Username and password does not match."))
            elif not self.user.check_password(password):
                raise forms.ValidationError(_("Password Does not Match."))
            if not self.user.is_active:
                raise forms.ValidationError(_("User is not Active."))
            

        return super(CustomLoginForm, self).clean(*args, **kwargs)

    def get_user(self):
        return self.user

