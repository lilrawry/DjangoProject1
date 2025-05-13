from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms_admin import UserForm, UserCreationForm

@login_required
def manage_users(request):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    users = User.objects.all().order_by('username')
    context = {
        'users': users,
        'title': 'Gestion des utilisateurs'
    }
    return render(request, 'rooms/admin_users.html', context)

@login_required
def add_user(request):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur ajouté avec succès!")
            return redirect('rooms:manage_users')
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
        'title': 'Ajouter un utilisateur'
    }
    return render(request, 'rooms/admin_user_form.html', context)

@login_required
def edit_user(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur mis à jour avec succès!")
            return redirect('rooms:manage_users')
    else:
        form = UserForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'title': 'Modifier l\'utilisateur'
    }
    return render(request, 'rooms/admin_user_form.html', context)

@login_required
def delete_user(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Utilisateur supprimé avec succès!")
        return redirect('rooms:manage_users')
    
    context = {
        'user': user,
        'title': 'Supprimer l\'utilisateur'
    }
    return render(request, 'rooms/admin_user_confirm_delete.html', context)
