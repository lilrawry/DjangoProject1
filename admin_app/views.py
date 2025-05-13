from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AdminLoginForm, AdminRegistrationForm

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = AdminLoginForm()
    return render(request, 'admin_app/login.html', {'form': form})

@login_required
def admin_dashboard(request):
    return render(request, 'admin_app/dashboard.html')

def admin_logout(request):
    from rooms.views import custom_logout
    return custom_logout(request)

def admin_register(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('admin_dashboard')
    else:
        form = AdminRegistrationForm()
    return render(request, 'admin_app/register.html', {'form': form}) 