from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg
from datetime import datetime, timedelta
from accounts.models import UserProfile

class Course(models.Model):
    """Model for online courses/live classes"""
    COURSE_TYPE_CHOICES = [
        ('live', 'Live Class'),
        ('recorded', 'Recorded Course'),
        ('hybrid', 'Hybrid'),
    ]
    
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/images/', blank=True, null=True)
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES, default='live')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Enhanced schedule details for live classes
    schedule_days = models.JSONField(default=list, blank=True)  # Store list of days: ['monday', 'wednesday', 'friday']
    start_time = models.TimeField(blank=True, null=True)  # e.g., 08:00:00
    end_time = models.TimeField(blank=True, null=True)  # e.g., 09:00:00
    session_details = models.TextField(blank=True)
    
    # For display purposes (backward compatibility)
    schedule_time = models.CharField(max_length=100, blank=True)  # e.g., "8:00 AM - 9:00 AM"
    
    # Course metadata
    duration = models.CharField(max_length=100, blank=True)  # e.g., "3 months"
    instructor_name = models.CharField(max_length=200, blank=True)
    
    # Live class specific
    meeting_link = models.URLField(blank=True, null=True)  # Zoom/Google Meet link
    class_start_date = models.DateField(blank=True, null=True)  # When course starts
    class_end_date = models.DateField(blank=True, null=True)  # When course ends
    
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
    
    def get_average_rating(self):
        """Get average rating from reviews"""
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 5.0
    
    def get_total_reviews(self):
        """Get total number of reviews"""
        return self.reviews.count()
    
    def get_full_stars(self):
        """Get number of full stars for display"""
        return int(self.get_average_rating())
    
    def has_half_star(self):
        """Check if rating has half star"""
        rating = self.get_average_rating()
        return (rating - int(rating)) >= 0.5
    
    def is_live_now(self):
        """Check if class is currently live"""
        if self.course_type != 'live' or not self.start_time or not self.end_time:
            return False
        
        now = timezone.localtime(timezone.now())
        current_time = now.time()
        current_day = now.strftime('%A').lower()
        
        # Check if today is a scheduled day
        if current_day not in self.schedule_days:
            return False
        
        # Check if within class time range
        return self.start_time <= current_time <= self.end_time
    
    def is_starting_soon(self, minutes=10):
        """Check if class is starting within specified minutes"""
        if self.course_type != 'live' or not self.start_time:
            return False
        
        now = timezone.localtime(timezone.now())
        current_time = now.time()
        current_day = now.strftime('%A').lower()
        
        # Check if today is a scheduled day
        if current_day not in self.schedule_days:
            return False
        
        # Convert times to datetime for comparison
        now_dt = datetime.combine(now.date(), current_time)
        class_start = datetime.combine(now.date(), self.start_time)
        
        # Check if class starts within the next X minutes
        time_diff = (class_start - now_dt).total_seconds() / 60
        return 0 <= time_diff <= minutes
    
    def get_next_class_datetime(self):
        """Get the next scheduled class datetime"""
        if self.course_type != 'live' or not self.start_time or not self.schedule_days:
            return None
        
        now = timezone.localtime(timezone.now())
        current_day = now.strftime('%A').lower()
        
        # Day order for finding next occurrence
        days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        try:
            current_day_index = days_order.index(current_day)
        except ValueError:
            return None
        
        # Check today first if class hasn't started yet
        if current_day in self.schedule_days:
            class_time = datetime.combine(now.date(), self.start_time)
            if now.time() < self.start_time:
                return timezone.make_aware(class_time)
        
        # Find next scheduled day
        for i in range(1, 8):
            next_day_index = (current_day_index + i) % 7
            next_day = days_order[next_day_index]
            
            if next_day in self.schedule_days:
                days_ahead = i
                next_date = now.date() + timedelta(days=days_ahead)
                next_datetime = datetime.combine(next_date, self.start_time)
                return timezone.make_aware(next_datetime)
        
        return None
    
    def get_class_status(self):
        """Get current status of the class"""
        if self.course_type != 'live':
            return 'recorded'
        
        if self.is_live_now():
            return 'live_now'
        elif self.is_starting_soon(10):
            return 'starting_soon'
        else:
            return 'scheduled'
    
    def minutes_until_class(self):
        """Get minutes until next class starts"""
        if self.course_type != 'live' or not self.start_time:
            return None
        
        now = timezone.localtime(timezone.now())
        current_time = now.time()
        current_day = now.strftime('%A').lower()
        
        if current_day in self.schedule_days:
            now_dt = datetime.combine(now.date(), current_time)
            class_start = datetime.combine(now.date(), self.start_time)
            
            if class_start > now_dt:
                time_diff = (class_start - now_dt).total_seconds() / 60
                return int(time_diff)
        
        return None

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
    
    # Notifications
    notified_10min = models.BooleanField(default=False)  # Track if 10-min notification sent
    last_notification_date = models.DateField(blank=True, null=True)  # Reset daily
    
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
    
    def reset_notification_if_new_day(self):
        """Reset notification flag if it's a new day"""
        today = timezone.localtime(timezone.now()).date()
        if self.last_notification_date != today:
            self.notified_10min = False
            self.last_notification_date = today
            self.save(update_fields=['notified_10min', 'last_notification_date'])

class CourseReview(models.Model):
    """Model for course reviews - only enrolled users can review"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
    enrollment = models.ForeignKey(CourseEnrollment, on_delete=models.CASCADE, related_name='review')
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['course', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.rating}⭐)"

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