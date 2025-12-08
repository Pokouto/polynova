from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Country(TimeStampedModel):
    """
    Représente un Pays avec sa configuration complète (CDC Section 13).
    """
    name = models.CharField(max_length=100, verbose_name="Nom")
    code = models.CharField(max_length=3, unique=True, verbose_name="Code ISO")
    currency_symbol = models.CharField(max_length=10, default="F CFA", verbose_name="Devise")
    is_active = models.BooleanField(default=False, verbose_name="Actif ?")
    
    # --- PARAMÈTRES FINANCIERS (CDC) ---
    subscription_price = models.IntegerField(default=3000, verbose_name="Prix Abo Prof (30j)")
    
    # Prix Contacts Parents (Liste séparée par virgules pour simplicité ou JSON)
    # Ex: 1500,2000,3500,5000,10000
    contact_prices = models.CharField(
        max_length=255, 
        default="1500,2000,3500,5000,10000", 
        help_text="Prix des contacts (Primaire, Collège, Lycée, Exam, Premium)"
    )
    
    # Seuils
    min_budget_threshold = models.IntegerField(default=30000, verbose_name="Seuil Budget Min (Scoring)")
    
    # --- PARAMÈTRES DÉLAIS (CDC) ---
    casier_delay_weeks = models.IntegerField(default=4, verbose_name="Délai Casier (Semaines)")
    relance_days = models.CharField(
        max_length=50, 
        default="3,7,10", 
        help_text="Jours de relance (ex: 3,7,10)"
    )

    def __str__(self):
        return f"{self.name} ({self.code})"
        
    class Meta:
        verbose_name = "Configuration Pays"
        verbose_name_plural = "Configurations Pays"

class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=100)
    def __str__(self): return self.name