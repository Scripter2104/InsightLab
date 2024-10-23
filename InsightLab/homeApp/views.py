from django.shortcuts import render
from .models import Test
from django.urls import reverse


# Create your views here.

def home_view(request, *ags, **kwargs):
    return render(request, 'home_page.html', {})


def newtest_view(request, *args, **kwargs):
    return render(request, 'new_test.html', {})


def test_start_page_config(request, *args, **kwargs):
    return render(request, 'test_start_page.html', {})


def question_manager_view(request, *args, **kwargs):
    return render(request, 'question_manager.html', {})


def start_test(request, *args, **kwargs):
    return render(request, 'start_test.html', {})


def grading_summary_view(request, *args, **kwargs):
    return render(request, 'grading_summary.html', {})


def time_setting_view(request,*args,**kwargs):
    return render(request,'time_setting.html',{})

def activate_test(request, test_id):
    test = Test.objects.get(id=test_id)

    if not test.name:
        return render(request, 'time_setting.html', {"message": "All field are nor filled!"})

    test.is_active = True
    test.link = request.build_absolute_uri(reverse('test_start_pa'))
