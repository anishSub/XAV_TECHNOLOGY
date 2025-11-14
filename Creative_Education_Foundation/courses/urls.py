
from django.urls import path
from .views import CoursesView, OnlineClassExtraView1, OnlineClassExtraView2,OnlineClassExtraView3,OnlineClassExtraView4,   EnrollmentInitiateView, PaymentConfirmView, EnrollmentSuccessView, live_classes_view,  online_classes_view, course_detail, submit_course_review, delete_course_review, all_courses_view, CourseDetailView, online_class_extra_redirect



urlpatterns = [
    # path('online-classes/', OnlineClassesView.as_view(), name='online_classes'),
    path('courses/', CoursesView.as_view(), name='courses'),
    path('online-classes/extra1/', OnlineClassExtraView1.as_view(), name='online_class_extra1'),
    path('online-classes/extra2/', OnlineClassExtraView2.as_view(), name='online_class_extra2'),
    path('online-classes/extra3/', OnlineClassExtraView3.as_view(), name='online_class_extra3'),
    path('online-classes/extra4/', OnlineClassExtraView4.as_view(), name='online_class_extra4'),
    # path('online-classes/enroll-now/', EnrollNowView.as_view(), name='enroll_now1'),
    
        # COURSE ENROLLMENT URLs
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('online-classes/<int:course_id>/enroll-now/', EnrollmentInitiateView.as_view(), name='enroll_now'),
    path('enrollment/<int:enrollment_id>/confirm/', PaymentConfirmView.as_view(), name='confirm_enrollment_payment'),
    path('enrollment/<int:enrollment_id>/success/', EnrollmentSuccessView.as_view(), name='enrollment_success'),
    
    
    path('live-classes/', live_classes_view, name='current_live_classes'),
    
    # All courses page (with filtering)
    path('courses/', all_courses_view, name='all_courses'),
    
    
    path('online-classes/', online_classes_view, name='online_classes'),
    
    # Course detail
    # path('course/<int:course_id>/', course_detail, name='course_detail'),
    
    path('online-classes/extra/<int:course_id>/',online_class_extra_redirect, name='online_class_extra'),
    
    # Review management
    path('course/<int:course_id>/review/', submit_course_review, name='submit_course_review'),
    
    path('course/<int:course_id>/review/delete/', delete_course_review, name='delete_course_review'),
]
