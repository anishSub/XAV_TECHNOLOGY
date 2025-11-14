from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Vacancy, VacancyApplication, PaymentLog
from courses.models import CoursePaymentLog, CourseEnrollment, Course
from accounts.models import UserProfile
from .models import Question



@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'question', 'answered', 'created_at']
    list_filter = ['answered', 'created_at']
    search_fields = ['name', 'email', 'question']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'employment_type', 'location', 'salary', 
                    'openings', 'deadline', 'is_active', 'applications_count']
    list_filter = ['employment_type', 'level', 'mode', 'is_active', 'created_at']
    search_fields = ['title', 'company_name', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company_name', 'employment_type', 'location')
        }),
        ('Job Details', {
            'fields': ('salary', 'level', 'mode', 'openings', 'start_date', 'deadline')
        }),
        ('Description', {
            'fields': ('description', 'requirements', 'responsibilities')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def applications_count(self, obj):
        count = obj.applications.count()
        url = reverse('admin:pages_vacancyapplication_changelist') + f'?vacancy__id__exact={obj.id}'
        return format_html('<a href="{}">{} applications</a>', url, count)
    applications_count.short_description = 'Applications'
    
    actions = ['activate_vacancies', 'deactivate_vacancies']
    
    def activate_vacancies(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} vacancies activated.')
    activate_vacancies.short_description = 'Activate selected vacancies'
    
    def deactivate_vacancies(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} vacancies deactivated.')
    deactivate_vacancies.short_description = 'Deactivate selected vacancies'


class PaymentLogInline(admin.TabularInline):
    model = PaymentLog
    extra = 0
    readonly_fields = ['transaction_id', 'amount', 'status', 'payment_method', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(VacancyApplication)
class VacancyApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'vacancy_title', 'status', 'payment_status', 
                    'payment_badge', 'applied_at']
    list_filter = ['status', 'payment_status', 'vacancy', 'applied_at']
    search_fields = ['full_name', 'email', 'phone', 'vacancy__title']
    readonly_fields = ['vacancy', 'full_name', 'email', 'phone', 'cv_link', 'cv_size', 
                       'khalti_transaction_id', 'khalti_payment_token', 'payment_date', 
                       'applied_at', 'updated_at']
    date_hierarchy = 'applied_at'
    inlines = [PaymentLogInline]
    
    fieldsets = (
        ('Application Details', {
            'fields': ('vacancy', 'full_name', 'email', 'phone')
        }),
        ('CV', {
            'fields': ('cv_link', 'cv_size')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
        ('Payment Information', {
            'fields': ('payment_status', 'payment_amount', 'khalti_transaction_id', 
                'khalti_payment_token', 'payment_date')
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def vacancy_title(self, obj):
        return obj.vacancy.title
    vacancy_title.short_description = 'Vacancy'
    vacancy_title.admin_order_field = 'vacancy__title'
    
    def cv_link(self, obj):
        if obj.cv:
            return format_html('<a href="{}" target="_blank">Download CV</a>', obj.cv.url)
        return '-'
    cv_link.short_description = 'CV File'
    
    def cv_size(self, obj):
        size_mb = obj.get_cv_size_mb()
        return f'{size_mb} MB'
    cv_size.short_description = 'CV Size'
    
    def payment_badge(self, obj):
        colors = {
            'completed': 'green',
            'pending': 'orange',
            'failed': 'red',
            'refunded': 'blue'
        }
        color = colors.get(obj.payment_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_badge.short_description = 'Payment'
    
    actions = ['mark_under_review', 'mark_shortlisted', 'mark_accepted', 'mark_rejected']
    
    def mark_under_review(self, request, queryset):
        updated = queryset.update(status='under_review')
        self.message_user(request, f'{updated} applications marked as under review.')
    mark_under_review.short_description = 'Mark as Under Review'
    
    def mark_shortlisted(self, request, queryset):
        updated = queryset.update(status='shortlisted')
        self.message_user(request, f'{updated} applications shortlisted.')
    mark_shortlisted.short_description = 'Mark as Shortlisted'
    
    def mark_accepted(self, request, queryset):
        updated = queryset.update(status='accepted')
        self.message_user(request, f'{updated} applications accepted.')
    mark_accepted.short_description = 'Mark as Accepted'
    
    def mark_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} applications rejected.')
    mark_rejected.short_description = 'Mark as Rejected'


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'application_name', 'amount', 'status', 
                    'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'application__full_name', 'application__email']
    readonly_fields = ['application', 'transaction_id', 'amount', 'status', 
                       'payment_method', 'response_data', 'created_at']
    date_hierarchy = 'created_at'
    
    def application_name(self, obj):
        return obj.application.full_name
    application_name.short_description = 'Applicant'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
