"""
Create this file in your app directory (same level as views.py)
Example: courses/context_processors.py
"""

def user_enrollment_status(request):
    """
    Context processor to check if user has active live class enrollments
    """
    has_active_live_class_enrollment = False
    
    if request.user.is_authenticated:
        from .models import CourseEnrollment
        
        # Check if user has any active enrollments for Live Classes
        has_active_live_class_enrollment = CourseEnrollment.objects.filter(
            user=request.user,
            is_active=True,
            payment_status='completed',
            course__course_type='live',  # Changed from 'Live Class' to 'live'
            course__is_active=True
        ).exists()
    
    return {
        'user': request.user,
        'has_active_live_class_enrollment': has_active_live_class_enrollment,
    }