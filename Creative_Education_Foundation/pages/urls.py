from django.urls import path
from .views import (
    AdminView, BaseView, HomeView, MockTestView,ProfileView,
    VacancyListView, VacancyDetailView, VacancyApplicationView,
    SimplePaymentView, ConfirmPaymentView, ApplicationSuccessView, MyApplicationsView
)

urlpatterns = [
    # Basic pages
    path('', HomeView.as_view(), name='home'),
    path('admin1/', AdminView.as_view(), name='admin'),
    path('base/', BaseView.as_view(), name='base'),

    path('mock-test/', MockTestView.as_view(), name='mock_test'),
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Online classes extra pages
   
    
    # VACANCIES - Clean URLs (NO DUPLICATES)
    path('vacancies/', VacancyListView.as_view(), name='vacancies'),
    path('vacancies/<int:pk>/', VacancyDetailView.as_view(), name='vacancies_description'),
    path('vacancies/<int:vacancy_id>/apply/', VacancyApplicationView.as_view(), name='vacancy_apply'),
    
    # PAYMENT
    path('payment/<int:application_id>/', SimplePaymentView.as_view(), name='khalti_payment'),
    path('payment/<int:application_id>/confirm/', ConfirmPaymentView.as_view(), name='confirm_payment'),
    
    # SUCCESS & MY APPLICATIONS
    path('application/<int:application_id>/success/', ApplicationSuccessView.as_view(), name='application_success'),
    path('my-applications/', MyApplicationsView.as_view(), name='my_applications'),
]