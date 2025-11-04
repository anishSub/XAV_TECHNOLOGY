from django import forms
from .models import VacancyApplication
from django.core.exceptions import ValidationError

class VacancyApplicationForm(forms.ModelForm):
    class Meta:
        model = VacancyApplication
        fields = ['full_name', 'email', 'phone', 'cv']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'id': 'fullName',
                'placeholder': 'Enter Your Name',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'id': 'email',
                'placeholder': 'Enter your valid email address',
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'id': 'phone',
                'placeholder': 'Enter your valid phone number',
                'class': 'form-control'
            }),
            'cv': forms.FileInput(attrs={
                'id': 'cv',
                'accept': '.pdf',
                'hidden': True
            }),
        }
    
    def clean_cv(self):
        cv = self.cleaned_data.get('cv')
        if cv:
            # Check file size (4MB = 4 * 1024 * 1024 bytes)
            if cv.size > 4 * 1024 * 1024:
                raise ValidationError('File size must not exceed 4MB.')
            
            # Check file extension
            if not cv.name.endswith('.pdf'):
                raise ValidationError('Only PDF files are allowed.')
        
        return cv
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Add phone number validation if needed
        # Example: Check if it's a valid Nepali number
        if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValidationError('Please enter a valid phone number.')
        return phone