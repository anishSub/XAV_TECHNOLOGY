from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    mobile_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'mobile_number', 'password1', 'password2']
        
        
    def clean_mobile_number(self):
        """Validate mobile number format"""
        mobile = self.cleaned_data.get('mobile_number')
        if not mobile.isdigit():
            raise ValidationError("Mobile number must contain only digits")
        if len(mobile) < 10:
            raise ValidationError("Mobile number must be at least 10 digits")
        return mobile

    def clean_email(self):
        """Check if email already exists"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered")
        return email

    def clean(self):
        """Custom validation for the entire form"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        # Password match is already validated by UserCreationForm
        # But you can add extra validations here
        if password1 and len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        
        return cleaned_data
    
    
