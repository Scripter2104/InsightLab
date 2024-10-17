from django.shortcuts import render


# Create your views here.

def home_view(request, *ags, **kwargs):
    return render(request, 'home_page.html', {})


def newtest_view(request, *args, **kwargs):
    return render(request, 'new_test.html', {})
