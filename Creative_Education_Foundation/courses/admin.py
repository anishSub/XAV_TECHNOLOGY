from django.contrib import admin

# Register your models here.
# Add to pages/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Course, CourseEnrollment, CoursePaymentLog, UserProfile, CourseReview


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'course_type', 'price', 'discount_percentage',  'schedule_display',   'is_active', 'enrollment_count',
        'get_average_rating', 
        'get_total_reviews', 
        'is_active', 
        'created_at']
    
    list_filter = ['course_type', 'is_active', 'created_at','schedule_days']
    search_fields = ['title', 'description', 'instructor_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'image', 'course_type')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_percentage')
        }),
        ('Schedule', {
            'fields': ('schedule_time', 'session_details', 'duration')
        }),
        ('Instructor', {
            'fields': ('instructor_name', )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def enrollment_count(self, obj):
        count = obj.enrollments.filter(payment_status='completed').count()
        return format_html('<strong>{}</strong> students', count)
    enrollment_count.short_description = 'Enrollments'
    
    actions = ['activate_courses', 'deactivate_courses']
    
    def activate_courses(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} courses activated.')
    activate_courses.short_description = 'Activate selected courses'
    
    def deactivate_courses(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} courses deactivated.')
    deactivate_courses.short_description = 'Deactivate selected courses'

    def schedule_display(self, obj):
        """Display schedule information"""
        if not obj.start_time or not obj.schedule_days:
            return '—'
        
        days = ', '.join([day.capitalize()[:3] for day in obj.schedule_days])
        time = f"{obj.start_time.strftime('%I:%M %p')}"
        if obj.end_time:
            time += f" - {obj.end_time.strftime('%I:%M %p')}"
        
        return format_html('{}<br><small>{}</small>', days, time)
    
    schedule_display.short_description = 'Schedule'
    
    
    def get_current_status(self, obj):
        """Readonly field showing current status"""
        if obj.course_type != 'live':
            return 'This is a recorded course'
        
        status = obj.get_class_status()
        next_class = obj.get_next_class_datetime()
        
        status_text = {
            'live_now': '🔴 Class is LIVE NOW!',
            'starting_soon': f'⏰ Starting in {obj.minutes_until_class()} minutes',
            'scheduled': '📅 Scheduled'
        }.get(status, 'Not scheduled')
        
        if next_class:
            status_text += f' | Next: {next_class.strftime("%a, %b %d at %I:%M %p")}'
        
        return status_text
    
    get_current_status.short_description = 'Current Status'
    
    def get_average_rating(self, obj):
        return f"{obj.get_average_rating()}⭐"
    get_average_rating.short_description = 'Avg Rating'
    
    def get_total_reviews(self, obj):
        return obj.get_total_reviews()
    get_total_reviews.short_description = 'Reviews'
    
    class Media:
        js = ('admin/js/course_schedule.js',)  # Optional: for better UX
        css = {
            'all': ('admin/css/course_admin.css',)
        }

class CoursePaymentLogInline(admin.TabularInline):
    model = CoursePaymentLog
    extra = 0
    readonly_fields = ['transaction_id', 'amount', 'payment_method', 'status', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False
    
    



@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'course_name', 'amount_paid', 'payment_status', 
                    'payment_method', 'enrolled_at', 'access_status','get_notification_status']
    
    list_filter = ['payment_status', 'payment_method', 'is_active', 'enrolled_at','notified_10min']
    
    search_fields = ['user__username', 'user__email', 'course__title', 'transaction_id']
    
    readonly_fields = ['user', 'course', 'amount_paid', 'transaction_id', 
    'enrolled_at', 'payment_date', 'last_notification_date']
    
    date_hierarchy = 'enrolled_at'
    inlines = [CoursePaymentLogInline]
    
    fieldsets = (
        ('Enrollment Details', {
            'fields': ('user', 'course', 'enrolled_at')
        }),
        ('Payment Information', {
            'fields': ('payment_status', 'payment_method', 'amount_paid', 
                      'transaction_id', 'payment_date')
        }),
        ('Access Control', {
            'fields': ('is_active', 'access_expiry')
        }),
        
        ('Notifications', {
            'fields': ('notified_10min', 'last_notification_date'),
            'classes': ('collapse',)
        }),
    )
    
    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = 'Student'
    user_name.admin_order_field = 'user__username'
    
    def course_name(self, obj):
        return obj.course.title
    course_name.short_description = 'Course'
    course_name.admin_order_field = 'course__title'
    
    def access_status(self, obj):
        if obj.has_access():
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Expired</span>'
        )
    access_status.short_description = 'Access'
    
    actions = ['mark_completed', 'mark_active', 'mark_inactive']
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(payment_status='completed')
        self.message_user(request, f'{updated} enrollments marked as completed.')
    mark_completed.short_description = 'Mark payment as completed'
    
    def mark_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} enrollments activated.')
    mark_active.short_description = 'Activate enrollments'
    
    def mark_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} enrollments deactivated.')
    mark_inactive.short_description = 'Deactivate enrollments'
    
    # def get_access_status(self, obj):
    #     if obj.has_access():
    #         return format_html(
    #             '<span style="color: white; background: #4CAF50; padding: 3px 10px; '
    #             'border-radius: 10px;">✓ Active</span>'
    #         )
    #     return format_html(
    #         '<span style="color: white; background: #f44336; padding: 3px 10px; '
    #         'border-radius: 10px;">✗ No Access</span>'
    #     )
    # get_access_status.short_description = 'Access Status'
    
    def get_notification_status(self, obj):
        if obj.notified_10min:
            return format_html('✓ Notified today')
        return '—'
    get_notification_status.short_description = 'Notification'
    
    actions = ['reset_notifications']
    
    def reset_notifications(self, request, queryset):
        """Admin action to reset notification flags"""
        updated = queryset.update(notified_10min=False)
        self.message_user(request, f'{updated} enrollment(s) notification reset.')
    reset_notifications.short_description = 'Reset 10-min notifications'




@admin.register(CoursePaymentLog)
class CoursePaymentLogAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'enrollment_user', 'amount', 'payment_method', 
                    'status', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['transaction_id', 'enrollment__user__username']
    readonly_fields = ['enrollment', 'transaction_id', 'amount', 'payment_method', 
                       'status', 'response_data', 'created_at']
    date_hierarchy = 'created_at'
    
    def enrollment_user(self, obj):
        return obj.enrollment.user.username
    enrollment_user.short_description = 'User'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'rating', 'has_comment', 'created_at', 'updated_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'course__title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Review Details', {
            'fields': ('user', 'course', 'enrollment', 'rating', 'comment')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def has_comment(self, obj):
        return bool(obj.comment)
    has_comment.boolean = True
    has_comment.short_description = 'Has Comment'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'mobile_number', 'enrolled_courses_count']
    search_fields = ['user__username', 'user__email', 'mobile_number']
    readonly_fields = ['user']
    
    def enrolled_courses_count(self, obj):
        count = CourseEnrollment.objects.filter(
            user=obj.user, 
            payment_status='completed'
        ).count()
        return format_html('<strong>{}</strong> courses', count)
    enrolled_courses_count.short_description = 'Enrolled Courses'