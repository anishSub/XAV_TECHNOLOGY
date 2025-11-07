
from django.urls import path
from .views import OnlineClassesView, CoursesView, OnlineClassExtraView1, OnlineClassExtraView2,OnlineClassExtraView3,OnlineClassExtraView4, EnrollNowView, CourseDetailView, EnrollmentInitiateView, PaymentConfirmView, EnrollmentSuccessView


urlpatterns = [
    path('online-classes/', OnlineClassesView.as_view(), name='online_classes'),
    path('courses/', CoursesView.as_view(), name='courses'),
    path('online-classes/extra1/', OnlineClassExtraView1.as_view(), name='online_class_extra1'),
    path('online-classes/extra2/', OnlineClassExtraView2.as_view(), name='online_class_extra2'),
    path('online-classes/extra3/', OnlineClassExtraView3.as_view(), name='online_class_extra3'),
    path('online-classes/extra4/', OnlineClassExtraView4.as_view(), name='online_class_extra4'),
    path('online-classes/enroll-now/', EnrollNowView.as_view(), name='enroll_now'),
    
        # COURSE ENROLLMENT URLs
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('course/<int:course_id>/enroll/', EnrollmentInitiateView.as_view(), name='enroll_course'),
    path('enrollment/<int:enrollment_id>/confirm/', PaymentConfirmView.as_view(), name='confirm_enrollment_payment'),
    path('enrollment/<int:enrollment_id>/success/', EnrollmentSuccessView.as_view(), name='enrollment_success'),
]
