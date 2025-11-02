from django.shortcuts import render
from django.views.generic import TemplateView

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
    

