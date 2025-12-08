from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.education.models import Subject, Level
from apps.core.models import City

class CourseRequest(models.Model):
    """
    Une annonce déposée par un parent pour trouver un professeur.
    Contient les critères de besoin, de budget et de scoring.
    """

    # --- 1. Statuts de la demande (CDC Section 12.1) ---
    STATUS_CHOICES = (
        ('active', 'Recherche en cours'),       # Visible par les profs
        ('consulting', 'En discussion'),        # Parent en contact
        ('closed', 'Conclue / Prof trouvé'),    # Demande terminée succès
        ('expired', 'Expirée'),                 # Aucune activité après délai
        ('abandoned', 'Abandonnée'),            # Annulée par le parent
    )

    # --- 2. Tranches de Budget (CDC Section 2.1.2 & 13) ---
    # Seuil "Intention Forte" à partir de 'standard' (30 000 F)
    BUDGET_CHOICES = (
        ('low', 'Moins de 20 000 F CFA'),
        ('medium_low', '20 000 - 30 000 F CFA'),
        ('standard', '30 000 - 50 000 F CFA'),
        ('high', '50 000 - 80 000 F CFA'),
        ('premium', 'Plus de 80 000 F CFA'),
    )

    # --- 3. Délai de démarrage (CDC Section 2.1.2 - Q5) ---
    START_TIME_CHOICES = (
        ('asap', 'Dès que possible (dans les 7 jours)'),
        ('1-4weeks', 'Dans 1 à 4 semaines'),
        ('later', 'Plus tard / Je ne sais pas encore'),
    )

    # --- 4. Intention (CDC Section 2.1.2 - Q8) ---
    INTENT_CHOICES = (
        ('start', 'Je veux démarrer des cours'),
        ('info', 'Je souhaite seulement des informations'),
    )

    # --- RELATIONS ---
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_requests', verbose_name="Parent")
    
    # --- LE BESOIN PÉDAGOGIQUE ---
    subjects = models.ManyToManyField(Subject, verbose_name="Matières souhaitées")
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, verbose_name="Niveau de l'élève")
    
    # --- LOGISTIQUE & LOCALISATION ---
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, verbose_name="Ville")
    quartier = models.CharField(max_length=100, verbose_name="Quartier précis")
    frequency = models.CharField(max_length=100, verbose_name="Fréquence (ex: 2x par semaine)")
    is_online = models.BooleanField(default=False, verbose_name="Accepte les cours en ligne (Visio)")
    
    # --- SCORING & QUALIFICATION (CDC Section 2.1.3) ---
    start_time = models.CharField(max_length=20, choices=START_TIME_CHOICES, default='asap', verbose_name="Délai de démarrage")
    intention = models.CharField(max_length=10, choices=INTENT_CHOICES, default='start', verbose_name="Intention actuelle")
    budget_range = models.CharField(max_length=20, choices=BUDGET_CHOICES, default='standard', verbose_name="Budget mensuel")
    
    # Champ calculé automatiquement par le système (Intention Forte / Tiède)
    qualification = models.CharField(max_length=50, blank=True, verbose_name="Qualification du Lead")

    description = models.TextField(verbose_name="Détails supplémentaires", blank=True)
    
    # --- GESTION ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Demande de cours"
        verbose_name_plural = "Demandes de cours"

    def __str__(self):
        return f"Demande {self.parent.username} - {self.level} ({self.get_status_display()})"


class Review(models.Model):
    """
    Avis laissé par un parent sur un professeur après avoir débloqué le contact.
    """
    tutor = models.ForeignKey('profiles.TutorProfile', on_delete=models.CASCADE, related_name='reviews', verbose_name="Professeur concerné")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_written', verbose_name="Auteur (Parent)")
    
    rating = models.IntegerField(
        verbose_name="Note /5",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=[(i, f"{i}/5") for i in range(1, 6)]
    )
    comment = models.TextField(verbose_name="Commentaire", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de l'avis")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Avis & Notation"
        verbose_name_plural = "Avis & Notations"

    def __str__(self):
        return f"Note {self.rating}/5 pour {self.tutor.user.username} par {self.author.username}"