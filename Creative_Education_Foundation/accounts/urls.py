from django.urls import path, include
from .views import CustomLoginView
from .views import RegisterView


urlpatterns = [
    # Your custom login view (this will override the default)
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    
    # Include the rest of Django's auth URLs (logout, password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
    
    path('register/', RegisterView.as_view(), name='register'),
]