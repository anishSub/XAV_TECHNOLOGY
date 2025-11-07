from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from .models import VacancyApplication


class VacancyApplicationForm(forms.ModelForm):
    """Form for vacancy applications"""
    
    class Meta:
        model = VacancyApplication
        fields = ['full_name', 'email', 'phone', 'cv']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Your Name',
                'id': 'fullName'
            }),
            
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your valid email address',
                'id': 'email'
            }),
            
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your valid phone number',
                'id': 'phone'
            }),
            
            'cv': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf',
                'id': 'cv'
            }),
        }
        labels = {
            'full_name': 'Full Name',
            'email': 'Email',
            'phone': 'Phone number',
            'cv': 'Upload CV',
        }
    
    def clean_cv(self):
        cv = self.cleaned_data.get('cv')

        if not cv:
            raise ValidationError("Please upload your CV file.")

    # Ensure cv is an uploaded file, not a model FieldFile
        if hasattr(cv, 'size'):
            file_size = cv.size
        elif hasattr(cv, 'file') and hasattr(cv.file, 'size'):
            file_size = cv.file.size
        else:
            raise ValidationError("Invalid file object. Please upload again.")

    # Convert bytes → MB
        size_mb = file_size / (1024 * 1024)

        if size_mb > 5:
            raise ValidationError("CV file size must not exceed 5MB.")

    # Optional: Only allow PDF uploads
        if not cv.name.lower().endswith('.pdf'):
            raise ValidationError("Only PDF files are allowed.")

        return cv

    
    def clean_phone(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone', '')
        phone = phone.replace(' ', '').replace('-', '')

        if not phone.isdigit():
            raise ValidationError('Phone number must contain only digits.')
        if len(phone) < 10:
            raise ValidationError('Phone number must be at least 10 digits.')
        return phone
    
    def clean_email(self):
        """Validate and normalize email"""
        email = self.cleaned_data.get('email')
        return email.lower() if email else email