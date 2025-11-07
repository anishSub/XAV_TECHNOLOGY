from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import Vacancy, VacancyApplication, PaymentLog
from .forms import VacancyApplicationForm


# ============= BASIC VIEWS =============
class AdminView(TemplateView):
    template_name = 'admin.html'
    
class BaseView(TemplateView):
    template_name = 'base.html'
    
class HomeView(TemplateView):
    template_name = 'home.html'



class MockTestView(TemplateView):
    template_name = 'mockTest.html'
    

    
    
    
    
    
    
    
    

class ProfileView(TemplateView):
    template_name = 'profile.html'


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