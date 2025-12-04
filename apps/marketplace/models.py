from django.db import models
from django.conf import settings
from apps.education.models import Subject, Level
from apps.core.models import City

class CourseRequest(models.Model):
    """
    Une annonce déposée par un parent.
    Ex: "Cherche prof de Maths pour 3ème à Cocody".
    """
    # Statuts de la demande (CDC)
    STATUS_CHOICES = (
        ('active', 'Recherche en cours'),
        ('consulting', 'En discussion'),
        ('closed', 'Professeur trouvé'),
        ('expired', 'Expirée'),
    )

    # Fourchettes de budget (CDC Côte d'Ivoire)
    BUDGET_CHOICES = (
        ('low', 'Moins de 20.000 FCFA'),
        ('medium', '20.000 - 30.000 FCFA'),
        ('standard', '30.000 - 50.000 FCFA'),
        ('high', '50.000 - 80.000 FCFA'),
        ('premium', 'Plus de 80.000 FCFA'),
    )

    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_requests')
    
    # Le Besoin
    subjects = models.ManyToManyField(Subject, verbose_name="Matières souhaitées")
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, verbose_name="Niveau de l'élève")
    
    # Logistique
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, verbose_name="Ville")
    quartier = models.CharField(max_length=100, verbose_name="Quartier précis")
    frequency = models.CharField(max_length=100, verbose_name="Fréquence (ex: 2x par semaine)")
    is_online = models.BooleanField(default=False, verbose_name="Accepte les cours en ligne")
    
    # Infos financières & Gestion
    budget_range = models.CharField(max_length=20, choices=BUDGET_CHOICES, default='standard')
    description = models.TextField(verbose_name="Détails du besoin", blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demande de {self.parent.username} ({self.level})"
    
    # ... (Gardez les imports existants)
from django.core.validators import MinValueValidator, MaxValueValidator # Pour borner la note entre 1 et 5

class Review(models.Model):
    """
    Avis laissé par un parent sur un professeur.
    """
    tutor = models.ForeignKey('profiles.TutorProfile', on_delete=models.CASCADE, related_name='reviews', verbose_name="Professeur concerné")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_written', verbose_name="Auteur (Parent)")
    
    rating = models.IntegerField(
        verbose_name="Note /5",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=[(i, f"{i}/5") for i in range(1, 6)]
    )
    comment = models.TextField(verbose_name="Commentaire", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Les plus récents en premier
        verbose_name = "Avis"
        verbose_name_plural = "Avis"

    def __str__(self):
        return f"Note {self.rating}/5 pour {self.tutor.user.username}"