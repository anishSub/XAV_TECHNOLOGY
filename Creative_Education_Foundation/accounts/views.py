from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm


# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('home') 
    
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        # Custom registration logic here if needed
        return super().form_valid(form)