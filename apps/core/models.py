from django.db import models

class TimeStampedModel(models.Model):
    """
    Un modèle de base. 
    Ajoute automatiquement la date de création à tout ce qui en hérite.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        abstract = True

class Country(TimeStampedModel):
    """
    Gestion des Pays (ex: Côte d'Ivoire).
    Contient les paramètres financiers paramétrables (CDC).
    """
    name = models.CharField(max_length=100, verbose_name="Nom du pays")
    code = models.CharField(max_length=3, unique=True, verbose_name="Code ISO (ex: CI)")
    currency_symbol = models.CharField(max_length=10, default="F CFA", verbose_name="Devise")
    
    is_active = models.BooleanField(default=False, verbose_name="Actif sur le site ?")
    
    # Paramètres financiers (CDC)
    min_budget_threshold = models.IntegerField(default=30000, verbose_name="Seuil Budget Min (Scoring)")
    subscription_price = models.IntegerField(default=3000, verbose_name="Prix Abonnement Prof")

    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        verbose_name = "Pays"
        verbose_name_plural = "Pays"

class City(models.Model):
    """Ville (ex: Abidjan)"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=100, verbose_name="Ville")

    def __str__(self):
        return self.name

class Quartier(models.Model):
    """Quartier ou Commune (ex: Cocody)"""
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="quartiers")
    name = models.CharField(max_length=100, verbose_name="Quartier/Commune")

    def __str__(self):
        return f"{self.name} ({self.city.name})"