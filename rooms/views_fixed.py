from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone
from io import BytesIO
from datetime import datetime
from .models import Room, Reservation, Payment

def home(request):
    """
    Simple home view to test if the server is working
    """
    return HttpResponse("<h1>Welcome to the Room Reservation System</h1>")

@login_required
def room_list(request):
    rooms = Room.objects.all().order_by('name')
    context = {
        'rooms': rooms,
        'title': 'Room List'
    }
    return render(request, 'rooms/room_list.html', context)

@login_required
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    context = {
        'room': room,
        'title': f'Details - {room.name}'
    }
    return render(request, 'rooms/room_detail.html', context)

@login_required
def create_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.save()
            messages.success(request, "Reservation created successfully!")
            return redirect('rooms:room_detail', pk=reservation.room.pk)
    else:
        form = ReservationForm()
    
    context = {
        'form': form,
        'title': 'Create Reservation'
    }
    return render(request, 'rooms/create_reservation.html', context)

@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-start_time')
    context = {
        'reservations': reservations,
        'title': 'My Reservations'
    }
    return render(request, 'rooms/my_reservations.html', context)

@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if reservation.status != 'pending':
        messages.error(request, "This reservation cannot be canceled.")
        return redirect('rooms:my_reservations')
    
    reservation.delete()
    messages.success(request, "Reservation canceled successfully!")
    return redirect('rooms:my_reservations')

@login_required
def download_pdf(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id, user=request.user)
    
    # Create context for PDF template
    context = {
        'reservation': reservation,
        'date': datetime.now().strftime('%d/%m/%Y')
    }
    
    # Render template to HTML
    template = get_template('rooms/reservation_pdf.html')
    html = template.render(context)
    
    # Create PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = FileResponse(result.getvalue(), content_type='application/pdf')
        filename = f'reservation_{reservation.id}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    return redirect('rooms:my_reservations')

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('rooms:room_list')
    
    stats = {
        'rooms': Room.objects.count(),
        'reservations': Reservation.objects.count(),
        'users': User.objects.count(),
        'pending_payments': Payment.objects.filter(status='pending').count(),
        'pending_reservations': Reservation.objects.filter(status='pending', is_paid=False).count()
    }
    
    context = {
        'stats': stats,
        'title': 'Admin Dashboard'
    }
    return render(request, 'rooms/admin_dashboard.html', context)

@login_required
def export_rooms_csv(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('rooms:room_list')
    
    return HttpResponse("<h2>Export Rooms CSV</h2>")

@login_required
def export_reservations_csv(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('rooms:room_list')
    
    return HttpResponse("<h2>Export Reservations CSV</h2>")

@login_required
def import_rooms_csv(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('rooms:room_list')
    
    return HttpResponse("<h2>Import Rooms CSV</h2>")

@login_required
def preview_csv_import(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('rooms:room_list')
    
    return HttpResponse("<h2>Preview CSV Import</h2>")

@login_required
def process_payment(request, reservation_id):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('rooms:room_list')
    
    return HttpResponse(f"<h2>Process Payment for reservation {reservation_id}</h2>")

@login_required
def approve_payment(request, payment_id):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('rooms:room_list')
    
    return HttpResponse(f"<h2>Approve Payment {payment_id}</h2>")

@login_required
def reject_payment(request, payment_id):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('rooms:room_list')
    
    return HttpResponse(f"<h2>Reject Payment {payment_id}</h2>")

@login_required
def approve_reservation(request, reservation_id):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('rooms:room_list')
    
    return HttpResponse(f"<h2>Approve Reservation {reservation_id}</h2>")

@login_required
def reject_reservation(request, reservation_id):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('rooms:room_list')
    
    return HttpResponse(f"<h2>Reject Reservation {reservation_id}</h2>")

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"You are logged in as {username}")
                return redirect('rooms:home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Login error. Please check your information.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'rooms/login.html', {'form': form})

@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('rooms:home')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect('rooms:home')
        else:
            messages.error(request, "Registration error. Please check your information.")
    else:
        form = UserCreationForm()
    
    return render(request, 'rooms/register.html', {'form': form})
