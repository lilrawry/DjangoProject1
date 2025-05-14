from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from .models import Room, Reservation, Payment
from django.db.models import Count, Sum, Q

@login_required
def admin_rooms(request):
    """View for managing all rooms"""
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    rooms = Room.objects.all().order_by('name')
    
    # Get statistics
    available_rooms = rooms.filter(is_available=True).count()
    unavailable_rooms = rooms.filter(is_available=False).count()
    
    # Get most reserved rooms
    most_reserved = Room.objects.annotate(
        reservation_count=Count('reservation')
    ).order_by('-reservation_count')[:5]
    
    context = {
        'rooms': rooms,
        'available_rooms': available_rooms,
        'unavailable_rooms': unavailable_rooms,
        'most_reserved': most_reserved,
        'title': 'Gestion des Salles'
    }
    return render(request, 'rooms/admin_dashboard/rooms.html', context)

@login_required
def admin_reservations(request):
    """View for managing all reservations"""
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    reservations = Reservation.objects.all().order_by('-created_at')
    
    # Get statistics
    pending_count = reservations.filter(status='pending').count()
    confirmed_count = reservations.filter(status='confirmed').count()
    cancelled_count = reservations.filter(status='cancelled').count()
    paid_count = reservations.filter(is_paid=True).count()
    unpaid_count = reservations.filter(is_paid=False).count()
    
    context = {
        'reservations': reservations,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'cancelled_count': cancelled_count,
        'paid_count': paid_count,
        'unpaid_count': unpaid_count,
        'title': 'Gestion des Réservations'
    }
    return render(request, 'rooms/admin_dashboard/reservations.html', context)

@login_required
def admin_users(request):
    """View for managing all users"""
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    users = User.objects.all().order_by('-date_joined')
    
    # Get statistics
    staff_count = users.filter(is_staff=True).count()
    active_count = users.filter(is_active=True).count()
    inactive_count = users.filter(is_active=False).count()
    
    # Get most active users (with most reservations)
    most_active = User.objects.annotate(
        reservation_count=Count('reservation')
    ).order_by('-reservation_count')[:5]
    
    context = {
        'users': users,
        'staff_count': staff_count,
        'active_count': active_count,
        'inactive_count': inactive_count,
        'most_active': most_active,
        'title': 'Gestion des Utilisateurs'
    }
    return render(request, 'rooms/admin_dashboard/users.html', context)

@login_required
def admin_groups(request):
    """View for managing all groups"""
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    groups = Group.objects.all().order_by('name')
    
    # Get statistics for each group
    group_stats = []
    for group in groups:
        user_count = group.user_set.count()
        group_stats.append({
            'group': group,
            'user_count': user_count
        })
    
    context = {
        'groups': groups,
        'group_stats': group_stats,
        'title': 'Gestion des Groupes'
    }
    return render(request, 'rooms/admin_dashboard/groups.html', context)

@login_required
def admin_pending_payments(request):
    """View for managing pending payments"""
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    pending_payments = Payment.objects.filter(status='pending').order_by('-payment_date')
    
    # Get statistics
    total_pending_amount = pending_payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'pending_payments': pending_payments,
        'total_pending_amount': total_pending_amount,
        'title': 'Paiements en Attente'
    }
    return render(request, 'rooms/admin_dashboard/pending_payments.html', context)

@login_required
def admin_pending_reservations(request):
    """View for managing pending reservations"""
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    pending_reservations = Reservation.objects.filter(status='pending').order_by('-created_at')
    
    # Get statistics
    total_pending_amount = pending_reservations.aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    context = {
        'pending_reservations': pending_reservations,
        'total_pending_amount': total_pending_amount,
        'title': 'Réservations en Attente'
    }
    return render(request, 'rooms/admin_dashboard/pending_reservations.html', context)
