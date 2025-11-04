from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import VacancyApplication

@admin.register(VacancyApplication)
class VacancyApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'email',
        'phone',
        'payment_status',
        'status',
        'applied_at'
    ]
    list_filter = [
        'payment_status',
        'status',
        'applied_at'
    ]
    search_fields = [
        'full_name',
        'email',
        'phone',
        'khalti_transaction_id'
    ]
    readonly_fields = [
        'applied_at',
        'updated_at',
        'khalti_transaction_id'
    ]
    fieldsets = (
        ('Applicant Information', {
            'fields': ('full_name', 'email', 'phone', 'cv')
        }),
        ('Payment Information', {
            'fields': ('payment_status', 'payment_amount', 'khalti_transaction_id')
        }),
        ('Application Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_cv_filename(self, obj):
        return obj.get_cv_filename()
    get_cv_filename.short_description = 'CV File'