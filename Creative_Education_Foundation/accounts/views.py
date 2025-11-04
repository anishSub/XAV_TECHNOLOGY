from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from .models import UserProfile
from django.contrib.auth.views import LogoutView
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect




# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('home')
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Try to find user by email
        try:
            from django.contrib.auth.models import User
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, self.template_name)
        
        # Authenticate with username
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            
            # Handle remember me
            if not request.POST.get('remember'):
                request.session.set_expiry(0)
            
            return redirect(self.get_success_url())
        else:
            messages.error(request, 'Invalid email or password')
            return render(request, self.template_name)
    
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        # The form's save() method already handles everything:
        # - Saves first_name, last_name, email to User
        # - Creates UserProfile with mobile_number
        response = super().form_valid(form)
        
        # Add success message
        messages.success(self.request, 'Registration successful! Please log in.')
        
        return response
    
    
class CustomLogoutView(LogoutView):
    next_page = 'home'
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)