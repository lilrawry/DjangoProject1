from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required

@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès!")
    return redirect('rooms:room_list')

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Vous êtes connecté en tant que {username}")
                return redirect('rooms:room_list')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            messages.error(request, "Erreur de connexion. Veuillez vérifier vos informations.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'rooms/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie! Vous êtes maintenant connecté.")
            return redirect('rooms:room_list')
        else:
            messages.error(request, "Erreur lors de l'inscription. Veuillez vérifier les informations.")
    else:
        form = UserCreationForm()
    
    return render(request, 'rooms/register.html', {'form': form})
