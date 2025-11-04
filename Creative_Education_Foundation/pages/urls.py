from django.urls import path
from .views import AdminView, BaseView, HomeView, OnlineClassesView, CoursesView, VacanciesView,MockTestView, VacanciesDiecriptionView, VacanciesFormView, OnlineClassExtraView1, OnlineClassExtraView2, OnlineClassExtraView3, OnlineClassExtraView4, EnrollNowView, PaymentInitiateView, PaymentSuccessView, PaymentFailureView, ProfileView



urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('admin1/', AdminView.as_view(), name='admin'),
    path('base/', BaseView.as_view(), name='base'),
    path('online-classes/', OnlineClassesView.as_view(), name='online_classes'),
    path('courses/', CoursesView.as_view(), name='courses'),
    path('mock-test/', MockTestView.as_view(), name='mock_test'),
    path('vacancies/', VacanciesView.as_view(), name='vacancies'),
    path('vacancies/description/', VacanciesDiecriptionView.as_view(), name='vacancies_description'),
    path('vacancies/apply/', VacanciesFormView.as_view(), name='vacancies_apply'),
    path('payment/initiate/<int:application_id>/', PaymentInitiateView.as_view(), name='payment_initiate'),
    path('payment/success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/failure/', PaymentFailureView.as_view(), name='payment_failure'),
    
    
    path('online-classes/extra1/', OnlineClassExtraView1.as_view(), name='online_class_extra1'),
    path('online-classes/extra2/', OnlineClassExtraView2.as_view(), name='online_class_extra2'),
    path('online-classes/extra3/', OnlineClassExtraView3.as_view(), name='online_class_extra3'),
    path('online-classes/extra4/', OnlineClassExtraView4.as_view(), name='online_class_extra4'),
    path('online-classes/enroll-now/', EnrollNowView.as_view(), name='enroll_now'),
    path('profile/', ProfileView.as_view(), name='profile'),
    
]
