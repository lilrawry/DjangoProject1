from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room
from .forms import RoomForm

@login_required
def manage_rooms(request):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    rooms = Room.objects.all().order_by('name')
    context = {
        'rooms': rooms,
        'title': 'Gestion des salles'
    }
    return render(request, 'rooms/admin_rooms.html', context)

@login_required
def add_room(request):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Salle ajoutée avec succès!")
            return redirect('rooms:manage_rooms')
    else:
        form = RoomForm()
    
    context = {
        'form': form,
        'title': 'Ajouter une salle'
    }
    return render(request, 'rooms/admin_room_form.html', context)

@login_required
def edit_room(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    room = get_object_or_404(Room, pk=pk)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Salle mise à jour avec succès!")
            return redirect('rooms:manage_rooms')
    else:
        form = RoomForm(instance=room)
    
    context = {
        'form': form,
        'room': room,
        'title': 'Modifier la salle'
    }
    return render(request, 'rooms/admin_room_form.html', context)

@login_required
def delete_room(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    room = get_object_or_404(Room, pk=pk)
    
    if request.method == 'POST':
        room.delete()
        messages.success(request, "Salle supprimée avec succès!")
        return redirect('rooms:manage_rooms')
    
    context = {
        'room': room,
        'title': 'Supprimer la salle'
    }
    return render(request, 'rooms/admin_room_confirm_delete.html', context)
