from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse, HttpResponseServerError, HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Room, Reservation, Payment
from .forms import ReservationForm, UserRegistrationForm, PaymentForm
from .utils import generate_reservation_receipt
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import csv
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import json
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import logging
import string
import random
import uuid
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os

# Calculate total price for a reservation
def calculate_total_price(price_per_hour, start_time, end_time):
    """
    Calculate the total price for a reservation based on duration and hourly rate
    """
    duration = (end_time - start_time).total_seconds() / 3600
    return float(price_per_hour) * duration

# Configure logging
logger = logging.getLogger(__name__)

def home(request):
    # Redirect to room_list view
    return redirect('rooms:room_list')

def handler500(request, *args, **argv):
    return render(request, '500.html', status=500)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès!')
    return redirect('login')

@login_required
def room_list(request):
    try:
        rooms = Room.objects.all().order_by('name')
        
        # Search functionality
        search_query = request.GET.get('search')
        if search_query:
            rooms = rooms.filter(name__icontains=search_query)
        
        min_capacity = request.GET.get('min_capacity')
        if min_capacity:
            try:
                min_capacity = int(min_capacity)
                rooms = rooms.filter(capacity__gte=min_capacity)
            except (ValueError, TypeError):
                messages.error(request, "La capacité minimale doit être un nombre entier.")
        
        max_price = request.GET.get('max_price')
        if max_price:
            try:
                max_price = float(max_price)
                rooms = rooms.filter(price_per_hour__lte=max_price)
            except (ValueError, TypeError):
                messages.error(request, "Le prix maximum doit être un nombre.")
        
        availability = request.GET.get('availability')
        if availability == 'available':
            rooms = rooms.filter(is_available=True)
        elif availability == 'occupied':
            rooms = rooms.filter(is_available=False)
        
        # Pagination
        paginator = Paginator(rooms, 6)  # Show 6 rooms per page
        page = request.GET.get('page')
        try:
            rooms = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page
            rooms = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results
            rooms = paginator.page(paginator.num_pages)
        
        context = {
            'rooms': rooms,
            'is_paginated': True,
            'page_obj': rooms,
            'title': 'Liste des Salles'
        }
        
        return render(request, 'rooms/room_list.html', context)
    except Exception as e:
        logger.error(f"Error in room_list view: {str(e)}")
        return HttpResponseServerError("Une erreur s'est produite lors du chargement de la page.")

@login_required
def room_detail(request, pk):
    try:
        room = get_object_or_404(Room, pk=pk)
        min_date_time = timezone.now()
        
        if request.method == 'POST':
            form = ReservationForm(request.POST)
            if form.is_valid():
                reservation = form.save(commit=False)
                reservation.room = room
                reservation.user = request.user
                reservation.total_price = form.cleaned_data['total_price']
                reservation.status = 'pending'
                
                try:
                    reservation.save()
                    messages.success(request, 'Réservation effectuée avec succès!')
                    return redirect('rooms:process_payment', reservation_id=reservation.id)
                except Exception as e:
                    logger.error(f"Error saving reservation: {str(e)}")
                    messages.error(request, 'Une erreur est survenue lors de la réservation.')
        else:
            initial_start = timezone.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            initial_end = initial_start + timedelta(hours=1)
            form = ReservationForm(initial={'start_time': initial_start, 'end_time': initial_end, 'room': room})
        
        context = {
            'room': room,
            'min_date_time': min_date_time,
            'form': form,
        }
        
        return render(request, 'rooms/room_detail.html', context)
    except Exception as e:
        logger.error(f"Error in room_detail view: {str(e)}")
        return HttpResponseServerError("Une erreur s'est produite lors du chargement de la page.")

@login_required
def create_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.status = 'pending'
            
            # Calculate total price
            from decimal import Decimal
            duration = (reservation.end_time - reservation.start_time).total_seconds() / 3600
            reservation.total_price = reservation.room.price_per_hour * Decimal(str(duration))
            
            reservation.save()
            messages.success(request, 'Réservation effectuée avec succès!')
            return redirect('rooms:process_payment', reservation_id=reservation.id)
    else:
        form = ReservationForm()
    
    context = {
        'form': form,
        'title': 'Nouvelle Réservation'
    }
    
    return render(request, 'rooms/create_reservation.html', context)

@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'reservations': reservations,
        'title': 'Mes Réservations'
    }
    return render(request, 'rooms/my_reservations.html', context)

@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if reservation.status != 'confirmed':
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, 'Réservation annulée avec succès!')
    else:
        messages.error(request, 'Impossible d\'annuler une réservation confirmée.')
    return redirect('rooms:my_reservations')

@login_required
def download_pdf(request, reservation_id):
    try:
        reservation = get_object_or_404(Reservation, pk=reservation_id)
        
        # Check if user is authorized (either the reservation owner or staff)
        if reservation.user != request.user and not request.user.is_staff:
            messages.error(request, "Vous n'êtes pas autorisé à accéder à ce document.")
            return redirect('rooms:room_list')
        
        # Generate PDF
        pdf_file = generate_reservation_receipt(reservation)
        
        # Create response with PDF
        response = HttpResponse(pdf_file, content_type='application/pdf')
        filename = f"reservation_{reservation.id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        messages.error(request, "Une erreur est survenue lors de la génération du PDF.")
        return redirect('rooms:my_reservations')

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    # Get statistics for dashboard
    total_rooms = Room.objects.count()
    total_reservations = Reservation.objects.count()
    total_users = User.objects.count()
    
    # Get queryset of pending reservations (not just count)
    pending_reservations_queryset = Reservation.objects.filter(status='pending').order_by('-created_at')
    pending_reservations_count = pending_reservations_queryset.count()
    
    confirmed_reservations = Reservation.objects.filter(status='confirmed').count()
    cancelled_reservations = Reservation.objects.filter(status='cancelled').count()
    
    # Stats dictionary for display in cards
    stats = {
        'rooms': total_rooms,
        'reservations': total_reservations,
        'users': total_users,
        'pending_reservations': pending_reservations_count
    }
    
    context = {
        'stats': stats,
        'total_rooms': total_rooms,
        'total_reservations': total_reservations,
        'total_users': total_users,
        'pending_reservations': pending_reservations_queryset,  # Pass the queryset, not the count
        'pending_reservations_count': pending_reservations_count,
        'confirmed_reservations': confirmed_reservations,
        'cancelled_reservations': cancelled_reservations,
        'title': 'Tableau de Bord Admin'
    }
    
    return render(request, 'rooms/admin_dashboard.html', context)

@login_required
def export_rooms_csv(request):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rooms.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nom', 'Capacité', 'Description', 'Prix par heure', 'Disponible', 'Équipements'])
    
    # Get all rooms
    rooms = Room.objects.all().order_by('id')
    
    # Add room data to CSV
    for room in rooms:
        # Convert amenities from JSON to string
        amenities_str = ', '.join(room.amenities) if room.amenities else ''
        
        writer.writerow([
            room.id,
            room.name,
            room.capacity,
            room.description,
            room.price_per_hour,
            'Oui' if room.is_available else 'Non',
            amenities_str
        ])
    
    return response

@login_required
def export_reservations_csv(request):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reservations.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Salle', 'Utilisateur', 'Date de début', 'Date de fin', 
        'Date de création', 'Statut', 'Prix total', 'Payé'
    ])
    
    # Get all reservations
    reservations = Reservation.objects.all().order_by('-created_at')
    
    # Add reservation data to CSV
    for reservation in reservations:
        writer.writerow([
            reservation.id,
            reservation.room.name,
            reservation.user.username,
            reservation.start_time.strftime('%Y-%m-%d %H:%M'),
            reservation.end_time.strftime('%Y-%m-%d %H:%M'),
            reservation.created_at.strftime('%Y-%m-%d %H:%M'),
            reservation.get_status_display(),
            reservation.total_price,
            'Oui' if reservation.is_paid else 'Non'
        ])
    
    return response

@login_required
def import_rooms_csv(request):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Check if it's a CSV file
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Le fichier doit être au format CSV.')
            return redirect('rooms:admin_dashboard')
        
        # Save the uploaded file temporarily
        file_path = default_storage.save(f'temp_csv/{csv_file.name}', ContentFile(csv_file.read()))
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        try:
            # Process the CSV file
            with open(full_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)  # Skip header row
                
                # Check header format
                required_headers = ['Nom', 'Capacité', 'Description', 'Prix par heure', 'Disponible', 'Équipements']
                if not all(h in header for h in required_headers):
                    messages.error(request, 'Format de fichier CSV invalide. Veuillez vérifier les en-têtes.')
                    return redirect('rooms:admin_dashboard')
                
                # Get column indices
                name_idx = header.index('Nom')
                capacity_idx = header.index('Capacité')
                description_idx = header.index('Description')
                price_idx = header.index('Prix par heure')
                available_idx = header.index('Disponible')
                amenities_idx = header.index('Équipements') if 'Équipements' in header else None
                
                # Process rows
                rooms_created = 0
                rooms_updated = 0
                errors = 0
                
                for row in reader:
                    try:
                        # Validate data
                        if len(row) < 5:  # At least 5 columns required
                            continue
                        
                        name = row[name_idx].strip()
                        if not name:
                            continue
                        
                        # Parse capacity
                        try:
                            capacity = int(row[capacity_idx])
                        except ValueError:
                            capacity = 0
                        
                        # Parse price
                        try:
                            price = float(row[price_idx].replace(',', '.'))
                        except ValueError:
                            price = 0
                        
                        # Parse availability
                        available_str = row[available_idx].lower()
                        is_available = available_str in ['oui', 'yes', 'true', '1']
                        
                        # Parse amenities
                        amenities = []
                        if amenities_idx is not None and amenities_idx < len(row):
                            amenities_str = row[amenities_idx]
                            if amenities_str:
                                amenities = [item.strip() for item in amenities_str.split(',')]
                        
                        # Create or update room
                        room, created = Room.objects.update_or_create(
                            name=name,
                            defaults={
                                'capacity': capacity,
                                'description': row[description_idx],
                                'price_per_hour': price,
                                'is_available': is_available,
                                'amenities': amenities
                            }
                        )
                        
                        if created:
                            rooms_created += 1
                        else:
                            rooms_updated += 1
                    
                    except Exception as e:
                        logger.error(f"Error importing room: {str(e)}")
                        errors += 1
                
                # Show results
                if rooms_created > 0 or rooms_updated > 0:
                    messages.success(
                        request, 
                        f'{rooms_created} salles créées, {rooms_updated} salles mises à jour, {errors} erreurs.'
                    )
                else:
                    messages.warning(request, 'Aucune salle n\'a été importée.')
        
        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            messages.error(request, f'Erreur lors du traitement du fichier: {str(e)}')
        
        finally:
            # Clean up the temporary file
            default_storage.delete(file_path)
    
    return redirect('rooms:admin_dashboard')

# Validate CSV row data
def validate_csv_content(row):
    """
    Validate the content of a CSV row for room import
    Returns a tuple (is_valid, error_message)
    """
    if len(row) < 5:
        return False, "Nombre de colonnes insuffisant"
    
    name = row[0].strip()
    if not name:
        return False, "Le nom est obligatoire"
    
    try:
        capacity = int(row[1])
        if capacity <= 0:
            return False, "La capacité doit être un nombre positif"
    except ValueError:
        return False, "La capacité doit être un nombre entier"
    
    try:
        price = float(row[3].replace(',', '.'))
        if price <= 0:
            return False, "Le prix doit être un nombre positif"
    except ValueError:
        return False, "Le prix doit être un nombre"
    
    return True, ""

@login_required
def preview_csv_import(request):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Check if it's a CSV file
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Le fichier doit être au format CSV.')
            return redirect('rooms:admin_dashboard')
        
        # Save the uploaded file temporarily
        file_path = default_storage.save(f'temp_csv/{csv_file.name}', ContentFile(csv_file.read()))
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        try:
            # Process the CSV file for preview
            preview_data = []
            validation_errors = []
            
            with open(full_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)  # Skip header row
                
                # Check header format
                required_headers = ['Nom', 'Capacité', 'Description', 'Prix par heure', 'Disponible']
                if not all(h in header for h in required_headers):
                    messages.error(request, 'Format de fichier CSV invalide. Veuillez vérifier les en-têtes.')
                    return redirect('rooms:admin_dashboard')
                
                # Preview first 10 rows
                for i, row in enumerate(reader):
                    if i >= 10:  # Limit preview to 10 rows
                        break
                    
                    # Validate row
                    is_valid, error_message = validate_csv_content(row)
                    
                    preview_data.append({
                        'row': row,
                        'is_valid': is_valid
                    })
                    
                    if not is_valid:
                        validation_errors.append(f"Ligne {i+2}: {error_message}")
            
            # Store the file path in session for later import
            request.session['csv_import_path'] = file_path
            
            context = {
                'preview_data': preview_data,
                'headers': header,
                'validation_errors': validation_errors,
                'file_name': csv_file.name,
                'title': 'Aperçu de l\'importation'
            }
            
            return render(request, 'rooms/preview_import.html', context)
        
        except Exception as e:
            logger.error(f"Error previewing CSV file: {str(e)}")
            messages.error(request, f'Erreur lors de l\'aperçu du fichier: {str(e)}')
            default_storage.delete(file_path)
    
    return redirect('rooms:admin_dashboard')

@login_required
def process_payment(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    
    # Check if user is authorized (either the reservation owner or staff)
    if reservation.user != request.user and not request.user.is_staff:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('rooms:room_list')
    
    # Check if reservation is already paid
    if reservation.is_paid:
        messages.info(request, "Cette réservation a déjà été payée.")
        return redirect('rooms:my_reservations')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.reservation = reservation
            payment.amount = reservation.total_price
            payment.user = request.user
            payment.status = 'pending'
            
            # Generate a unique reference number
            payment.reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            
            # Generate a unique transaction ID using UUID
            payment.transaction_id = str(uuid.uuid4())
            
            payment.save()
            
            # Update reservation status
            reservation.status = 'pending'
            reservation.save()
            
            # Use a specific message format that will be detected by our JavaScript
            payment_message = "Votre paiement a été enregistré et est en attente d'approbation par un administrateur. Vous recevrez une confirmation une fois qu'il sera approuvé."
            # Add 'payment-message' as an extra tag to help identify this message in the template
            messages.success(request, payment_message, extra_tags='payment-message')
            return redirect('rooms:my_reservations')
    else:
        form = PaymentForm()
    
    context = {
        'reservation': reservation,
        'form': form,
        'title': 'Paiement'
    }
    
    return render(request, 'rooms/payment.html', context)

@login_required
def approve_payment(request, payment_id):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    payment = get_object_or_404(Payment, pk=payment_id)
    payment.status = 'completed'
    payment.save()
    
    # Update reservation status
    reservation = payment.reservation
    reservation.is_paid = True
    reservation.status = 'confirmed'  # Keep the traditional 'confirmed' status
    reservation.save()
    
    # Generate receipt PDF and redirect to display/download
    messages.success(request, "Paiement approuvé avec succès. Génération du reçu en cours...")
    
    # Redirect to the download PDF view with the reservation ID
    return redirect('rooms:download_pdf', reservation_id=reservation.id)

@login_required
def reject_payment(request, payment_id):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    payment = get_object_or_404(Payment, pk=payment_id)
    payment.status = 'rejected'
    payment.save()
    
    messages.success(request, "Paiement rejeté.")
    return redirect('rooms:admin_dashboard')

@login_required
def approve_reservation(request, reservation_id):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    reservation.status = 'confirmed'  # Keep the traditional 'confirmed' status for consistent UI display
    reservation.is_paid = True  # Also mark as paid when admin approves
    reservation.save()
    
    # Generate receipt PDF and redirect to display/download
    messages.success(request, "Réservation approuvée avec succès. Génération du reçu en cours...")
    
    # Redirect to the download PDF view with the reservation ID
    return redirect('rooms:download_pdf', reservation_id=reservation.id)

@login_required
def reject_reservation(request, reservation_id):
    if not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('rooms:room_list')
    
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    reservation.status = 'cancelled'
    reservation.save()
    
    messages.success(request, "Réservation rejetée.")
    return redirect('rooms:admin_dashboard')

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
                messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")
        else:
            messages.error(request, "Formulaire invalide. Veuillez vérifier vos informations.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'rooms/login.html', {'form': form})
