"""
URL configuration for InsightLab project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from loginApp.views import login_view
from loginApp.views import signup_view
from homeApp.views import home_view, newtest_view, test_start_page_config, question_manager_view, grading_summary_view, start_test_view, time_setting_view, activate_test

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('home/', home_view, name='home'),
    path('newtest/basic setting', newtest_view, name='newtest'),
    path('newtest/test start page/', test_start_page_config, name='test_start_page'),
    path('newtest/question manager/', question_manager_view, name='question_manager'),
    path('newtest/grading and summary', grading_summary_view, name='grading_and_summary'),
    path('newtest/time setting', time_setting_view, name='time_setting'),
    path('InsightLab/<uuid:test_id>/', start_test_view, name='InsightLab'),
    path('newtest/activate_test/', activate_test, name='activate_test'),

]
