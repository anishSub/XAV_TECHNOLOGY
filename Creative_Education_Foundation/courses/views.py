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
from django.shortcuts import render
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from .models import Course, CourseEnrollment
from datetime import datetime

from accounts.models import UserProfile
from .models import Course, CourseEnrollment, CoursePaymentLog
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from .models import Course, CourseEnrollment
from .models import CourseReview
from django.shortcuts import render
from django.db.models import Avg, Count
from .models import Course



# Create your views here.

    
class CoursesView(TemplateView):
    template_name = 'courses.html'


def online_classes_view(request):
    """
    Display all active courses (live, recorded, and hybrid) with ratings.
    Shows all courses from the courses section.
    """
    # Get all active courses regardless of type
    courses = Course.objects.filter(
        is_active=True
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        total_reviews=Count('reviews')
    ).order_by('-created_at')  # Most recent first
    
    # Add user enrollment info if authenticated
    if request.user.is_authenticated:
        from .models import CourseEnrollment
        user_enrolled_ids = CourseEnrollment.objects.filter(
            user=request.user,
            payment_status='completed',
            is_active=True
        ).values_list('course_id', flat=True)
        
        # Add enrollment flag to each course
        for course in courses:
            course.is_user_enrolled = course.id in user_enrolled_ids
    else:
        for course in courses:
            course.is_user_enrolled = False
    
    context = {
        'courses': courses,
        'total_courses': courses.count(),
    }
    

    featured = (Course.objects
        .filter(is_active=True,
        course_type='live')
        .annotate(avg_rating=Avg('reviews__rating'))
        .order_by('-created_at')[:4])   # 4 live courses

    context['featured_courses'] = featured
    
    return render(request, 'live_classes/onlineClass.html', context)


def course_detail(request, course_id):
    """Display course details"""
    course = get_object_or_404(Course, id=course_id, is_active=True)
    
    # Check if user is enrolled
    is_enrolled = False
    user_enrollment = None
    user_review = None
    
    if request.user.is_authenticated:
        try:
            user_enrollment = CourseEnrollment.objects.get(
                user=request.user, 
                course=course,
                payment_status='completed'
            )
            is_enrolled = user_enrollment.has_access()
            
            # Check if user has already reviewed
            try:
                user_review = CourseReview.objects.get(user=request.user, course=course)
            except CourseReview.DoesNotExist:
                pass
        except CourseEnrollment.DoesNotExist:
            pass
    
    # Get all reviews
    reviews = course.reviews.select_related('user').order_by('-created_at')
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'user_enrollment': user_enrollment,
        'user_review': user_review,
        'reviews': reviews,
    }
    return render(request, 'courses/course_detail.html', context)




@login_required
def submit_course_review(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # --- 1.  must be enrolled ------------------------------
    enrollment = get_object_or_404(
        CourseEnrollment,
        user=request.user,
        course=course,
        payment_status='completed'
    )
    if not enrollment.has_access():
        messages.error(request, 'You need active enrollment to review this course.')
        return redirect('course_detail', pk=course_id)

    # --- 2.  already reviewed?  refuse ---------------------
    if CourseReview.objects.filter(user=request.user, course=course).exists():
        messages.info(request, 'You have already reviewed this course.')
        return redirect('course_detail', pk=course_id)

    # --- 3.  normal flow -----------------------------------
    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '').strip()

    if not rating or not rating.isdigit() or int(rating) not in range(1, 6):
        messages.error(request, 'Please provide a valid rating (1-5 stars).')
        return redirect('course_detail', pk=course_id)

    CourseReview.objects.create(
        user=request.user,
        course=course,
        enrollment=enrollment,
        rating=int(rating),
        comment=comment
    )
    messages.success(request, 'Thank you for your review!')
    return redirect('live_classes/onlineClass.html', pk=course_id)



@login_required
def delete_course_review(request, course_id):
    """Delete user's review for a course"""
    if request.method != 'POST':
        return redirect('course_detail', course_id=course_id)
    
    course = get_object_or_404(Course, id=course_id)
    
    try:
        review = CourseReview.objects.get(user=request.user, course=course)
        review.delete()
        messages.success(request, 'Your review has been deleted.')
    except CourseReview.DoesNotExist:
        messages.error(request, 'Review not found.')
    
    return redirect('course_detail', pk=course_id)

    
    


class OnlineClassExtraView1(DetailView):
    model = Course
    template_name = 'live_classes/onlineClass1.html'
    context_object_name = 'course'

    def get_object(self):
        return get_object_or_404(Course, id=1)   # change as needed

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # existing enrolment checks
        if self.request.user.is_authenticated:
            enrollment = CourseEnrollment.objects.filter(
                user=self.request.user,
                course=self.object,
                payment_status='completed'
            ).first()
            context['is_enrolled'] = enrollment is not None
            context['enrollment'] = enrollment
        else:
            context['is_enrolled'] = False
            context['enrollment'] = None

        context['discounted_price'] = self.object.get_discounted_price()

        # related courses with real average
        from django.db.models import Avg
        related = (Course.objects
                        .filter(is_active=True)
                        .annotate(avg_rating=Avg('reviews__rating'))
                        .exclude(id=self.object.id))[:3]
        context['related_courses'] = related

        return context

class OnlineClassExtraView2(DetailView):
    model = Course
    template_name = 'live_classes/onlineClass2.html'
    context_object_name = 'course'
    
    def get_object(self):
        return get_object_or_404(Course, id=2)  # Update this ID based on your database
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            enrollment = CourseEnrollment.objects.filter(
                user=self.request.user,
                course=self.object,
                payment_status='completed'
            ).first()
            context['is_enrolled'] = enrollment is not None
            context['enrollment'] = enrollment
        else:
            context['is_enrolled'] = False
            context['enrollment'] = None
        context['discounted_price'] = self.object.get_discounted_price()
        
        from django.db.models import Avg
        related = (Course.objects
                        .filter(is_active=True)
                        .annotate(avg_rating=Avg('reviews__rating'))
                        .exclude(id=self.object.id))[:3]
        context['related_courses'] = related
        return context

class OnlineClassExtraView3(DetailView):
    model = Course
    template_name = 'live_classes/onlineClass3.html'
    context_object_name = 'course'
    
    def get_object(self):
        return get_object_or_404(Course, id=3)  # Update this ID based on your database
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            enrollment = CourseEnrollment.objects.filter(
                user=self.request.user,
                course=self.object,
                payment_status='completed'
            ).first()
            context['is_enrolled'] = enrollment is not None
            context['enrollment'] = enrollment
        else:
            context['is_enrolled'] = False
            context['enrollment'] = None
        context['discounted_price'] = self.object.get_discounted_price()
        
        from django.db.models import Avg
        related = (Course.objects
                        .filter(is_active=True)
                        .annotate(avg_rating=Avg('reviews__rating'))
                        .exclude(id=self.object.id))[:3]
        context['related_courses'] = related
        return context

class OnlineClassExtraView4(DetailView):
    model = Course
    template_name = 'live_classes/onlineClass4.html'
    context_object_name = 'course'
    
    def get_object(self):
        return get_object_or_404(Course, id=4)  # Update this ID based on your database
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            enrollment = CourseEnrollment.objects.filter(
                user=self.request.user,
                course=self.object,
                payment_status='completed'
            ).first()
            context['is_enrolled'] = enrollment is not None
            context['enrollment'] = enrollment
        else:
            context['is_enrolled'] = False
            context['enrollment'] = None
        context['discounted_price'] = self.object.get_discounted_price()
        
        from django.db.models import Avg
        related = (Course.objects
                        .filter(is_active=True)
                        .annotate(avg_rating=Avg('reviews__rating'))
                        .exclude(id=self.object.id))[:3]
        context['related_courses'] = related
        
        return context
    



def live_classes_view(request):
    """
    Display all active live classes with real-time status.
    Shows classes that are:
    - Currently live
    - Starting soon (within 10 minutes)
    - Scheduled for today
    - Upcoming on scheduled days
    """
    now = timezone.localtime(timezone.now())
    current_time = now.time()
    current_day = now.strftime('%A').lower()
    
    # Get all active live classes
    all_live_classes = Course.objects.filter(
        is_active=True,
        course_type='live'
    ).order_by('start_time')
    
    # Categorize courses
    live_now = []
    starting_soon = []
    today_classes = []
    upcoming_classes = []
    
    # User's enrollments for notification purposes
    user_enrolled_course_ids = []
    if request.user.is_authenticated:
        user_enrolled_course_ids = list(
            CourseEnrollment.objects.filter(
                user=request.user,
                payment_status='completed',
                is_active=True
            ).values_list('course_id', flat=True)
        )
    
    for course in all_live_classes:
        # Skip if no schedule set
        if not course.start_time or not course.schedule_days:
            continue
        
        status = course.get_class_status()
        
        # Add enrollment info
        course.is_user_enrolled = course.id in user_enrolled_course_ids
        course.minutes_left = course.minutes_until_class()
        
        if status == 'live_now':
            live_now.append(course)
            # Send notification for enrolled users
            if request.user.is_authenticated and course.is_user_enrolled:
                messages.info(request, f'🔴 LIVE NOW: "{course.title}" is currently in session!')
        
        elif status == 'starting_soon':
            starting_soon.append(course)
            # Send 10-minute warning for enrolled users
            if request.user.is_authenticated and course.is_user_enrolled:
                minutes = course.minutes_left
                if minutes:
                    # Check if we should send notification
                    try:
                        enrollment = CourseEnrollment.objects.get(
                            user=request.user,
                            course=course
                        )
                        enrollment.reset_notification_if_new_day()
                        
                        if not enrollment.notified_10min:
                            messages.warning(
                                request,
                                f'⏰ Starting Soon: "{course.title}" starts in {minutes} minutes!'
                            )
                            enrollment.notified_10min = True
                            enrollment.save(update_fields=['notified_10min'])
                    except CourseEnrollment.DoesNotExist:
                        pass
        
        elif current_day in course.schedule_days:
            today_classes.append(course)
        else:
            upcoming_classes.append(course)
    
    # Combine all courses in priority order
    courses = live_now + starting_soon + today_classes + upcoming_classes
    
    context = {
        'courses': courses,
        'live_now': live_now,
        'starting_soon': starting_soon,
        'today_classes': today_classes,
        'upcoming_classes': upcoming_classes,
        'current_time': now,
    }
    
    return render(request, 'live_classes/current_live_classes.html', context)





def online_class_extra_redirect(request, course_id):
    """
    Redirect to the correct numbered extra view based on course id.
    Add as many mappings as you have.
    """
    # map course-pk → named url
    mapping = {
        1: 'online_class_extra1',
        2: 'online_class_extra2',
        3: 'online_class_extra3',
        4: 'online_class_extra4',
    }
    url_name = mapping.get(course_id, 'online_classes')  # fallback
    return redirect(url_name)




def get_user_upcoming_classes(user):
    """
    Get upcoming classes for enrolled user (for dashboard/notifications)
    """
    if not user.is_authenticated:
        return []
    
    now = timezone.localtime(timezone.now())
    
    # Get user's enrolled courses
    enrolled_courses = Course.objects.filter(
        enrollments__user=user,
        enrollments__payment_status='completed',
        enrollments__is_active=True,
        is_active=True,
        course_type='live'
    ).distinct()
    
    upcoming = []
    for course in enrolled_courses:
        status = course.get_class_status()
        if status in ['live_now', 'starting_soon']:
            upcoming.append({
                'course': course,
                'status': status,
                'minutes_left': course.minutes_until_class(),
                'next_class': course.get_next_class_datetime()
            })
    
    return sorted(upcoming, key=lambda x: x['minutes_left'] or 999)



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
    template_name = 'profile.html'
    context_object_name = 'enrollments'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return CourseEnrollment.objects.filter(
            user=self.request.user,
            payment_status='completed'
        ).select_related('course').order_by('-enrolled_at')


def all_courses_view(request):
    """
    Display all courses with filtering options
    """
    course_type = request.GET.get('type', None)
    search_query = request.GET.get('q', None)
    
    courses = Course.objects.filter(is_active=True)
    
    # Filter by course type if specified
    if course_type:
        courses = courses.filter(course_type=course_type)
    
    # Search functionality
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(instructor_name__icontains=search_query)
        )
    
    courses = courses.order_by('-created_at')
    
    # Add user enrollment info if authenticated
    if request.user.is_authenticated:
        user_enrolled_ids = CourseEnrollment.objects.filter(
            user=request.user,
            payment_status='completed',
            is_active=True
        ).values_list('course_id', flat=True)
        
        # Add enrollment flag to each course
        for course in courses:
            course.is_user_enrolled = course.id in user_enrolled_ids
    else:
        for course in courses:
            course.is_user_enrolled = False
    
    context = {
        'courses': courses,
        'course_type': course_type,
        'search_query': search_query,
    }
    
    return render(request, 'live_classes/onlineClass.html', context)