from django.db import models
from django.conf import settings
from apps.education.models import Subject, Level
from apps.core.models import City  # Import indispensable pour la ville

class ParentProfile(models.Model):
    """
    Profil dédié aux Parents/Élèves.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent_profile')
    is_phone_verified = models.BooleanField(default=False, verbose_name="Téléphone vérifié ?")
    address = models.CharField(max_length=255, blank=True, verbose_name="Adresse (Quartier/Ville)")

    def __str__(self):
        return f"Parent: {self.user.username}"


class TutorProfile(models.Model):
    """
    Profil Enseignant complet.
    """
    STATUS_CHOICES = (
        ('draft', 'Brouillon - Incomplet'),
        ('pending', 'En attente de validation'),
        ('validated', 'Validé - Visible'),
        ('rejected', 'Rejeté'),
        ('suspended', 'Suspendu'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tutor_profile')
    
    # --- 1. Infos Publiques ---
    bio = models.TextField(verbose_name="Biographie", help_text="Présentez-vous aux parents.")
    photo = models.ImageField(upload_to='tutors/photos/', verbose_name="Photo de profil")
    
    # --- 2. Localisation (NOUVEAU) ---
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ville de résidence")
    quartier = models.CharField(max_length=100, blank=True, verbose_name="Quartier / Commune")

    # --- 3. Documents (Privé) ---
    cni_document = models.FileField(upload_to='secure/identity/', blank=True, verbose_name="CNI / Passeport")
    casier_judiciaire = models.FileField(upload_to='secure/legal/', blank=True, verbose_name="Casier Judiciaire")
    diplomes_file = models.FileField(upload_to='secure/diplomas/', blank=True, verbose_name="Diplômes")

    # --- 4. Compétences ---
    subjects = models.ManyToManyField(Subject, related_name='tutors', blank=True, verbose_name="Matières")
    levels = models.ManyToManyField(Level, related_name='tutors', blank=True, verbose_name="Niveaux")
    
    is_online_class = models.BooleanField(default=False, verbose_name="Accepte cours en ligne")
    is_home_class = models.BooleanField(default=True, verbose_name="Accepte cours à domicile")

    # --- 5. Gestion ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")
    admin_notes = models.TextField(blank=True, verbose_name="Note Admin")
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Prof: {self.user.username} [{self.get_status_display()}]"

    def is_visible(self):
        return self.status == 'validated'