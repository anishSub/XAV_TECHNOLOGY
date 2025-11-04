

# Create your models here.
from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils import timezone

class VacancyApplication(models.Model):
    # Basic Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # CV Upload
    cv = models.FileField(
        upload_to='applications/cvs/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text='Upload your CV in PDF format (max 4MB)'
    )
    
    # Payment Information
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=100.00
    )
    khalti_transaction_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    
    # Metadata
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Application Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('submitted', 'Submitted'),
            ('under_review', 'Under Review'),
            ('shortlisted', 'Shortlisted'),
            ('rejected', 'Rejected'),
            ('accepted', 'Accepted'),
        ],
        default='submitted'
    )
    
    class Meta:
        ordering = ['-applied_at']
        verbose_name = 'Vacancy Application'
        verbose_name_plural = 'Vacancy Applications'
    
    def __str__(self):
        return f"{self.full_name} - {self.email}"
    
    def get_cv_filename(self):
        """Return just the filename without the path"""
        if self.cv:
            return self.cv.name.split('/')[-1]
        return None