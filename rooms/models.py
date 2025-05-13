from django.db import models
from django.conf import settings

class Room(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    capacity = models.IntegerField(verbose_name="Capacité")
    description = models.TextField(verbose_name="Description")
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix par heure")
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    image = models.ImageField(upload_to='room_images/', null=True, blank=True, verbose_name="Image")
    amenities = models.JSONField(default=list, verbose_name="Équipements")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Salle"
        verbose_name_plural = "Salles"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée')
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Salle")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Utilisateur")
    start_time = models.DateTimeField(verbose_name="Heure de début")
    end_time = models.DateTimeField(verbose_name="Heure de fin")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut"
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix total")
    is_paid = models.BooleanField(default=False, verbose_name="Payé")

    def __str__(self):
        return f"{self.room.name} - {self.user.username} - {self.start_time.date()}"

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé')
    ]
    
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name='payment_info',
        verbose_name="Réservation"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending',
        verbose_name="Statut du paiement"
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Date du paiement")
    payment_method = models.CharField(max_length=50, verbose_name="Méthode de paiement")
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name="ID de transaction")

    def __str__(self):
        return f"Paiement {self.transaction_id} - {self.status}"

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"