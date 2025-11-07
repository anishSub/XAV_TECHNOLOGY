from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView, ListView
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from .models import Course, CourseEnrollment, CoursePaymentLog, UserProfile



# Create your views here.

class OnlineClassesView(TemplateView):
    template_name = 'live_classes/onlineClass.html'
    
class CoursesView(TemplateView):
    template_name = 'courses.html'
    
    
class OnlineClassExtraView1(TemplateView):
    template_name = 'live_classes/onlineClass1.html'
    
class OnlineClassExtraView2(TemplateView):
    template_name = 'live_classes/onlineClass2.html'
    
class OnlineClassExtraView3(TemplateView):
    template_name = 'live_classes/onlineClass3.html'

class OnlineClassExtraView4(TemplateView):
    template_name = 'live_classes/onlineClass4.html'
    
    

    
    
class EnrollNowView(TemplateView):
    template_name = 'live_classes/enroll_now.html'
    



class CourseDetailView(DetailView):
    """Display course details"""
    model = Course
    template_name = 'live_classes/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if user is already enrolled
        if self.request.user.is_authenticated:
            context['is_enrolled'] = CourseEnrollment.objects.filter(
                user=self.request.user,
                course=self.object,
                payment_status='completed'
            ).exists()
        else:
            context['is_enrolled'] = False
        
        context['discounted_price'] = self.object.get_discounted_price()
        return context


@method_decorator(login_required, name='dispatch')
class EnrollmentInitiateView(View):
    """Initiate course enrollment"""
    template_name = 'live_classes/enroll_now.html'
    
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, is_active=True)
        
        # Check if already enrolled
        existing_enrollment = CourseEnrollment.objects.filter(
            user=request.user,
            course=course,
            payment_status='completed'
        ).first()
        
        if existing_enrollment:
            messages.info(request, 'You are already enrolled in this course.')
            return redirect('profile')
        
        # Check for pending enrollment
        pending_enrollment = CourseEnrollment.objects.filter(
            user=request.user,
            course=course,
            payment_status='pending'
        ).first()
        
        if not pending_enrollment:
            # Create new enrollment
            pending_enrollment = CourseEnrollment.objects.create(
                user=request.user,
                course=course,
                amount_paid=course.get_discounted_price(),
                payment_status='pending'
            )
        
        context = {
            'course': course,
            'enrollment': pending_enrollment,
            'discounted_price': course.get_discounted_price(),
            'discount': course.price - course.get_discounted_price(),
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class PaymentConfirmView(View):
    """Confirm payment for course enrollment"""
    
    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(CourseEnrollment, id=enrollment_id, user=request.user)
        
        if enrollment.payment_status == 'completed':
            messages.info(request, 'Payment already completed.')
            return redirect('profile')
        
        payment_method = request.POST.get('payment_method', 'manual')
        transaction_id = request.POST.get('transaction_id', f'MANUAL_{enrollment.id}_{timezone.now().strftime("%Y%m%d%H%M%S")}')
        
        with transaction.atomic():
            enrollment.payment_status = 'completed'
            enrollment.payment_method = payment_method
            enrollment.payment_date = timezone.now()
            enrollment.transaction_id = transaction_id
            # Set access expiry to 1 year from now
            enrollment.access_expiry = timezone.now() + timedelta(days=365)
            enrollment.save()
            
            # Log payment
            CoursePaymentLog.objects.create(
                enrollment=enrollment,
                transaction_id=transaction_id,
                amount=enrollment.amount_paid,
                payment_method=payment_method,
                status='completed',
                response_data={'note': 'Payment confirmed'}
            )
        
        messages.success(request, f'Successfully enrolled in {enrollment.course.title}!')
        return redirect('enrollment_success', enrollment_id=enrollment.id)


@method_decorator(login_required, name='dispatch')
class EnrollmentSuccessView(DetailView):
    """Success page after enrollment"""
    model = CourseEnrollment
    template_name = 'live_classes/enrollment_success.html'
    context_object_name = 'enrollment'
    pk_url_kwarg = 'enrollment_id'
    
    def get_queryset(self):
        return CourseEnrollment.objects.filter(user=self.request.user)


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """User profile with enrolled courses"""
    template_name = 'profile.html'
    
    def get(self, request):
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Get enrolled courses
        enrollments = CourseEnrollment.objects.filter(
            user=request.user,
            payment_status='completed'
        ).select_related('course').order_by('-enrolled_at')
        
        context = {
            'user': request.user,
            'profile': profile,
            'enrollments': enrollments,
        }
        return render(request, self.template_name, context)


class MyCourses(ListView):
    """List all courses user is enrolled in"""
    model = CourseEnrollment
    template_name = 'live_classes/my_courses.html'
    context_object_name = 'enrollments'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return CourseEnrollment.objects.filter(
            user=self.request.user,
            payment_status='completed'
        ).select_related('course').order_by('-enrolled_at')