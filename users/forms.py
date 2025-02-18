from django import forms
from django.contrib.auth.models import User
from .models import ContactMessage
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm

# Base Form to apply styling to all fields
class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

# User Registration Form
class UserRegisterForm(BaseForm, UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

# User Update Form
class UserUpdateForm(BaseForm, forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

# Contact Form
class ContactForm(BaseForm, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message', 'subject']


class CustomSetPasswordForm(SetPasswordForm):
    """
    Custom password reset form that only includes new password fields.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Custom form for changing password that includes old password verification.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})


# Profile Update Form
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['password']  # Optional, might be omitted if not needed
