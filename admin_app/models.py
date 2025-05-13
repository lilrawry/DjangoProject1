from django.db import models
from django.contrib.auth.models import AbstractUser

class Administrateur(AbstractUser):
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=15, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Administrateur"
        verbose_name_plural = "Administrateurs"

    def __str__(self):
        return self.username 