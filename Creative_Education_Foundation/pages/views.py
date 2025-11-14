from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile  # Adjust import if needed
from courses.models import CourseEnrollment  # Adjust import if needed

from .models import Vacancy, VacancyApplication, PaymentLog
from .forms import VacancyApplicationForm

from courses.views import online_classes_view
from courses.models import Course

from django.contrib import messages
from .models import Question
from django.views.decorators.http import require_http_methods



# ============= BASIC VIEWS =============
class AdminView(TemplateView):
    template_name = 'admin.html'
    
class BaseView(TemplateView):
    template_name = 'base.html'
    
from django.db.models import Avg   # put at top with other imports

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # live courses + real average rating
        context['featured_courses'] = (
            Course.objects
            .filter(is_active=True, course_type='live')
            .annotate(avg_rating=Avg('reviews__rating'))
            .order_by('-created_at')[:4]
        )
        context['faqs'] = Question.objects.filter(answered=True).order_by('-created_at')[:10]
        return context



class MockTestView(TemplateView):
    template_name = 'mockTest.html'
    

    


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    template_name = 'profile.html'
    
    def get(self, request):
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        context = {
            'user': request.user,
            'profile': profile,
        }
        return render(request, self.template_name, context)

@method_decorator(login_required, name='dispatch')
class MyCourses(ListView):
    model = CourseEnrollment
    template_name = 'my_courses.html'  # Or 'live_classes/my_courses.html' if in a subfolder
    context_object_name = 'enrollments'
    
    def get_queryset(self):
        return CourseEnrollment.objects.filter(
            user=self.request.user,
            payment_status='completed'
        ).select_related('course').order_by('-enrolled_at')
        


@login_required 
@require_http_methods(["POST"])
#Ask Question View
def submit_question(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        question = request.POST.get('question')
        suggestions = request.POST.get('suggestions')

        # Save the question to the database
        Question.objects.create(
            name=name,
            email=email,
            question=question,
            suggestions=suggestions,
            answered=False
        )

        messages.success(request, 'Your question has been submitted successfully!')
        return redirect('home')

    return render(request, 'home.html')


# ============= VACANCY VIEWS =============
class VacancyListView(ListView):
    """List all active vacancies"""
    model = Vacancy
    template_name = 'vacancies/vacancies_list.html'
    context_object_name = 'vacancies'
    paginate_by = 10
    
    def get_queryset(self):
        return Vacancy.objects.filter(is_active=True).order_by('-created_at')


class VacancyDetailView(DetailView):
    """Display single vacancy details"""
    model = Vacancy
    template_name = 'vacancies/vacancies_description.html'
    context_object_name = 'vacancy'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_deadline_passed'] = self.object.is_deadline_passed()
        return context


class VacancyApplicationView(View):
    """Handle vacancy application form"""
    template_name = 'vacancies/vacancies_apply.html'
    
    def get(self, request, vacancy_id):
        vacancy = get_object_or_404(Vacancy, id=vacancy_id, is_active=True)
        
        if vacancy.is_deadline_passed():
            messages.error(request, 'The application deadline has passed.')
            return redirect('vacancies_description', pk=vacancy_id)
        
        form = VacancyApplicationForm()
        
        context = {
            'form': form,
            'vacancy': vacancy,
            'application_fee': 100.00,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, vacancy_id):
        vacancy = get_object_or_404(Vacancy, id=vacancy_id, is_active=True)
        
        if vacancy.is_deadline_passed():
            messages.error(request, 'The application deadline has passed.')
            return redirect('vacancies_description', pk=vacancy_id)
        
        form = VacancyApplicationForm(request.POST, request.FILES)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            if VacancyApplication.objects.filter(vacancy=vacancy, email=email).exists():
                messages.error(request, 'You have already applied for this position.')
                return redirect('vacancies_description', pk=vacancy_id)
            
            application = form.save(commit=False)
            application.vacancy = vacancy
            application.payment_status = 'pending'
            application.save()
            
            messages.success(request, 'Application saved. Please complete the payment.')
            return redirect('khalti_payment', application_id=application.id)
        
        context = {
            'form': form,
            'vacancy': vacancy,
            'application_fee': 100.00,
        }
        return render(request, self.template_name, context)


# ============= PAYMENT VIEWS =============
class SimplePaymentView(TemplateView):
    """Simple payment page"""
    template_name = 'vacancies/simple_payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application_id = kwargs.get('application_id')
        application = get_object_or_404(VacancyApplication, id=application_id)
        
        context.update({
            'application': application,
            'amount': application.payment_amount,
        })
        return context


class ConfirmPaymentView(View):
    """Confirm payment"""
    
    def post(self, request, application_id):
        application = get_object_or_404(VacancyApplication, id=application_id)
        
        if application.payment_status == 'completed':
            messages.info(request, 'Payment already completed.')
            return redirect('application_success', application_id=application.id)
        
        with transaction.atomic():
            application.payment_status = 'completed'
            application.payment_date = timezone.now()
            application.khalti_transaction_id = f'MANUAL_{application.id}_{timezone.now().strftime("%Y%m%d%H%M%S")}'
            application.save()
            
            PaymentLog.objects.create(
                application=application,
                transaction_id=application.khalti_transaction_id,
                amount=application.payment_amount,
                status='completed',
                payment_method='manual',
                response_data={'note': 'Manual payment confirmation'}
            )
        
        messages.success(request, 'Payment confirmed successfully!')
        return redirect('application_success', application_id=application.id)


class ApplicationSuccessView(TemplateView):
    """Success page after payment"""
    template_name = 'vacancies/application_success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application_id = kwargs.get('application_id')
        application = get_object_or_404(VacancyApplication, id=application_id)
        
        context['application'] = application
        return context


class MyApplicationsView(ListView):
    """View user's applications"""
    model = VacancyApplication
    template_name = 'vacancies/my_applications.html'
    context_object_name = 'applications'
    
    def get_queryset(self):
        email = self.request.GET.get('email')
        if email:
            return VacancyApplication.objects.filter(email=email).order_by('-applied_at')
        return VacancyApplication.objects.none()