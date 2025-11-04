from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import VacancyApplicationForm
from .models import VacancyApplication
import json

# Create your views here.
#What is TemplateView?
# It is a ready-made Django class (django.views.generic.base.TemplateView).
# It already contains all the logic you would otherwise write by hand in a function such as:
# def home(request):
#     return render(request, 'home.html', {})
class AdminView(TemplateView):
    template_name = 'admin.html'
    
class BaseView(TemplateView):
    template_name = 'base.html'
    
class HomeView(TemplateView):
    template_name = 'home.html'

class OnlineClassesView(TemplateView):
    template_name = 'live_classes/onlineClass.html'
    
class CoursesView(TemplateView):
    template_name = 'courses.html'

class MockTestView(TemplateView):
    template_name = 'mockTest.html'
    
class VacanciesView(TemplateView):
    template_name = 'vacancies/vacancies.html'
    
class VacanciesDiecriptionView(TemplateView):
    template_name = 'vacancies/vacancies_description.html'
    
class VacanciesFormView(TemplateView):
    template_name = 'vacancies/vacancies_apply.html'
    
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
    
    


class VacanciesFormView(FormView):
    template_name = 'vacancies/vacancies_apply.html'
    form_class = VacancyApplicationForm
    success_url = reverse_lazy('payment_success')  # Change to your success URL
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context if needed
        return context
    
    def form_valid(self, form):
        try:
            # Save the application but don't commit yet
            application = form.save(commit=False)
            
            # Here you would integrate with Khalti payment
            # For now, we'll just save the application
            application.payment_status = 'pending'
            application.payment_amount = 100.00
            application.save()
            
            # Store application ID in session for payment verification
            self.request.session['application_id'] = application.id
            
            # Redirect to Khalti payment or success page
            messages.success(
                self.request,
                f'Application submitted successfully! Application ID: {application.id}'
            )
            
            # Here you would redirect to Khalti payment gateway
            # For now, redirecting to success page
            return redirect('payment_initiate', application_id=application.id)
            
        except Exception as e:
            messages.error(
                self.request,
                f'An error occurred while submitting your application: {str(e)}'
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Please correct the errors below and try again.'
        )
        return super().form_invalid(form)


# Payment related views
class PaymentInitiateView(TemplateView):
    """View to initiate Khalti payment"""
    template_name = 'vacancies/payment_initiate.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application_id = self.kwargs.get('application_id')
        
        try:
            application = VacancyApplication.objects.get(id=application_id)
            context['application'] = application
            context['amount'] = int(application.payment_amount * 100)  # Khalti uses paisa
        except VacancyApplication.DoesNotExist:
            messages.error(self.request, 'Application not found.')
        
        return context


class PaymentSuccessView(TemplateView):
    """View to handle successful payment"""
    template_name = 'vacancies/payment_success.html'
    
    def get(self, request, *args, **kwargs):
        # Get payment details from Khalti callback
        transaction_id = request.GET.get('transaction_id')
        application_id = request.session.get('application_id')
        
        if application_id and transaction_id:
            try:
                application = VacancyApplication.objects.get(id=application_id)
                application.payment_status = 'completed'
                application.khalti_transaction_id = transaction_id
                application.save()
                
                messages.success(
                    request,
                    'Payment successful! Your application has been submitted.'
                )
            except VacancyApplication.DoesNotExist:
                messages.error(request, 'Application not found.')
        
        return super().get(request, *args, **kwargs)


class PaymentFailureView(TemplateView):
    """View to handle failed payment"""
    template_name = 'vacancies/payment_failure.html'
    
    def get(self, request, *args, **kwargs):
        application_id = request.session.get('application_id')
        
        if application_id:
            try:
                application = VacancyApplication.objects.get(id=application_id)
                application.payment_status = 'failed'
                application.save()
                
                messages.error(
                    request,
                    'Payment failed. Please try again.'
                )
            except VacancyApplication.DoesNotExist:
                pass
        
        return super().get(request, *args, **kwargs)


class ProfileView(TemplateView):
    template_name = 'profile.html'