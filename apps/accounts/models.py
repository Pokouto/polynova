from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Notre utilisateur sur mesure.
    On remplace l'email par le téléphone comme identifiant principal si besoin,
    mais ici on garde username pour simplifier, avec un champ Rôle.
    """
    
    ROLE_CHOICES = (
        ('admin', 'Administrateur'),
        ('parent', 'Parent / Élève'),
        ('tutor', 'Enseignant'),
    )

    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='parent',
        verbose_name="Rôle"
    )

    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    
    # Lien vers le pays de résidence
    country = models.ForeignKey(
        'core.Country', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Pays"
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"