from django.shortcuts import render


# Create your views here.
def login_view(request, *args, **kwargs):
    return render(request, 'login_page.html', {})


def signup_view(request, *args, **kwargs):
    return render(request, 'signup_page.html', {})
