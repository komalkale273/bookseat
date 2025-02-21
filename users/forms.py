from django import forms
from django.contrib.auth.models import User
from .models import ContactMessage
from django.contrib.auth.forms import SetPasswordForm,  UserCreationForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import PasswordChangeForm
from .models import FAQ
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



# Profile Update Form
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['password']  # Optional, might be omitted if not needed
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter your email"})
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter new password"})
    )
    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm new password"})
    )
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter current password"})
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter new password"})
    )
    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm new password"})
    )
class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question']