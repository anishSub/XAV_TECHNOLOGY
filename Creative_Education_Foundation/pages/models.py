from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone



# models.py
class Question(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    question = models.TextField()
    suggestions = models.TextField(blank=True, null=True)
    answered = models.BooleanField(default=False)
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Question by {self.name}"




def validate_cv_size(file):
    """Validate CV file size (max 4MB)"""
    max_size = 4 * 1024 * 1024  # 4 MB
    if file.size > max_size:
        raise ValidationError("File size must be under 4 MB.")





class Vacancy(models.Model):
    """Model for job vacancies"""
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full-Time'),
        ('part_time', 'Part-Time'),
        ('contract', 'Contract'),
    ]
    
    LEVEL_CHOICES = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
    ]
    
    MODE_CHOICES = [
        ('onsite', 'On-site'),
        ('hybrid', 'Hybrid'),
        ('remote', 'Remote'),
    ]
    
    title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, default='CREATIVE EDUCATION FOUNDATION PVT. LTD')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='part_time')
    location = models.CharField(max_length=200, default='Pokhara')
    salary = models.DecimalField(max_digits=10, decimal_places=2, help_text='Monthly salary in Rs.')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='mid')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='hybrid')
    openings = models.PositiveIntegerField(default=1)
    start_date = models.DateField()
    deadline = models.DateField()
    description = models.TextField()
    requirements = models.TextField(help_text='Job requirements (one per line)')
    responsibilities = models.TextField(help_text='Job responsibilities (one per line)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Vacancies'
    
    def __str__(self):
        return f"{self.title} - {self.company_name}"
    
    def is_deadline_passed(self):
        return timezone.now().date() > self.deadline


class VacancyApplication(models.Model):
    """Model for vacancy applications"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    vacancy = models.ForeignKey(
        Vacancy, 
        on_delete=models.CASCADE, 
        related_name='applications'
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    cv = models.FileField(
        upload_to='applications/cvs/%Y/%m/',
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
            validate_cv_size,
        ]
    )
    
    # Application status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment details
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    khalti_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    khalti_payment_token = models.CharField(max_length=200, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Admin notes
    admin_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-applied_at']
        unique_together = ['vacancy', 'email']  # One application per email per vacancy
    
    def __str__(self):
        return f"{self.full_name} - {self.vacancy.title}"
    
    def get_cv_size_mb(self):
        """Return CV file size in MB"""
        if self.cv:
            return round(self.cv.size / (1024 * 1024), 2)
        return 0


class PaymentLog(models.Model):
    """Model to log all payment transactions"""
    application = models.ForeignKey(
        VacancyApplication, 
        on_delete=models.CASCADE, 
        related_name='payment_logs'
    )
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50, default='khalti')
    response_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_id} - {self.status}"