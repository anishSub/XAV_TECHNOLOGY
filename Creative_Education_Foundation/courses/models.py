from django.db import models

# Create your models here.
# Add these models to your pages/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Course(models.Model):
    """Model for online courses/live classes"""
    COURSE_TYPE_CHOICES = [
        ('live', 'Live Class'),
        ('recorded', 'Recorded Course'),
        ('hybrid', 'Hybrid'),
    ]
    
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/images/', blank=True, null=True)
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES, default='live')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Schedule details
    schedule_time = models.CharField(max_length=100, blank=True)  # e.g., "8:00 AM - 9:00 AM"
    session_details = models.TextField(blank=True)
    
    # Course metadata
    duration = models.CharField(max_length=100, blank=True)  # e.g., "3 months"
    instructor_name = models.CharField(max_length=200, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_discounted_price(self):
        """Calculate price after discount"""
        if self.discount_percentage > 0:
            discount_amount = (self.price * self.discount_percentage) / 100
            return self.price - discount_amount
        return self.price


class CourseEnrollment(models.Model):
    """Model for course enrollments"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('esewa', 'eSewa'),
        ('khalti', 'Khalti'),
        ('manual', 'Manual'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    
    # Payment details
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=200, blank=True, null=True)
    
    # Enrollment details
    enrolled_at = models.DateTimeField(auto_now_add=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    access_expiry = models.DateTimeField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-enrolled_at']
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    def has_access(self):
        """Check if user has active access to the course"""
        if not self.is_active or self.payment_status != 'completed':
            return False
        if self.access_expiry and timezone.now() > self.access_expiry:
            return False
        return True


class CoursePaymentLog(models.Model):
    """Log all payment transactions for courses"""
    enrollment = models.ForeignKey(CourseEnrollment, on_delete=models.CASCADE, related_name='payment_logs')
    transaction_id = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    response_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_id} - {self.status}"


class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    mobile_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"