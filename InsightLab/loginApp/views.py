from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomUserCreationForm


# Create your views here.
def signup_view(request):
    """Handle signup form submission and render the signup page."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup_page.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form_data = {
            'username': request.POST['username'],
            'password': request.POST['password']
        }
        user = authenticate(request, **form_data)
        if user is not None:
            login(request, user)
            request.session.set_expiry(3*60*60*24)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login_page.html', {'error': 'Invalid credentials.'})

    return render(request, 'login_page.html', {})
