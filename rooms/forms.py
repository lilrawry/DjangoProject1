from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Reservation, Room, Payment
from django.utils import timezone
import datetime

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'capacity', 'description', 'price_per_hour', 'is_available', 'image', 'amenities']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'amenities': forms.CheckboxSelectMultiple()
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.Select(choices=[
                ('credit_card', 'Carte de crédit'),
                ('paypal', 'PayPal'),
                ('bank_transfer', 'Virement bancaire'),
                ('cash', 'Espèces')
            ])
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['room', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(is_available=True)
        self.fields['room'].empty_label = "Sélectionnez une salle"
        
        # Format datetime fields if initial values are provided
        if 'initial' in kwargs and kwargs['initial']:
            if 'start_time' in kwargs['initial']:
                kwargs['initial']['start_time'] = kwargs['initial']['start_time'].strftime('%Y-%m-%dT%H:%M')
            if 'end_time' in kwargs['initial']:
                kwargs['initial']['end_time'] = kwargs['initial']['end_time'].strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        room = cleaned_data.get('room')

        if start_time and end_time and room:
            # Convert string inputs to datetime if needed
            if isinstance(start_time, str):
                start_time = datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
            if isinstance(end_time, str):
                end_time = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M')

            # Check if room is available during the selected time
            if not room.is_available:
                self.add_error('room', 'Cette salle n\'est pas disponible.')

            # Check if the selected time overlaps with existing reservations
            overlapping_reservations = Reservation.objects.filter(
                room=room,
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            if overlapping_reservations.exists():
                self.add_error('room', 'Cette salle est déjà réservée pour ces heures.')

            # Check minimum duration
            min_duration = datetime.timedelta(minutes=30)
            if end_time - start_time < min_duration:
                self.add_error('end_time', 'La réservation doit durer au moins 30 minutes.')

            # Check if start time is in the past
            if start_time < timezone.now():
                self.add_error('start_time', 'La date de début ne peut pas être dans le passé.')

            # Check if end time is before start time
            if end_time <= start_time:
                self.add_error('end_time', 'L\'heure de fin doit être après l\'heure de début.')

            # Check if start time is too far in the future
            max_future = timezone.now() + datetime.timedelta(days=30)
            if start_time > max_future:
                self.add_error('start_time', 'Les réservations ne peuvent pas être faites plus de 30 jours à l\'avance.')

        return cleaned_data