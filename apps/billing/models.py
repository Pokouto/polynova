from django.db import models
from django.conf import settings
from apps.profiles.models import TutorProfile

class ContactUnlock(models.Model):
    """
    Enregistre le fait qu'un Parent a payé pour voir les infos d'un Prof.
    C'est la table de liaison "Achat".
    """
    parent_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='unlocked_contacts')
    tutor_profile = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name='unlocked_by')
    
    amount_paid = models.IntegerField(verbose_name="Montant payé (FCFA)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # On empêche d'acheter 2 fois le même contact
        unique_together = ('parent_user', 'tutor_profile')
        verbose_name = "Déblocage Contact"
        verbose_name_plural = "Déblocages Contacts"

    def __str__(self):
        return f"{self.parent_user.username} -> {self.tutor_profile.user.username} ({self.amount_paid} FCFA)"