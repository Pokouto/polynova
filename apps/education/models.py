from django.db import models

class Level(models.Model):
    """
    Niveau scolaire (ex: CM2, 3ème, Terminale C).
    On ajoute un champ 'order' pour pouvoir trier correctement (CP avant CE1).
    """
    CATEGORY_CHOICES = (
        ('primaire', 'Primaire'),
        ('college', 'Collège'),
        ('lycee', 'Lycée'),
        ('superieur', 'Supérieur / Adulte'),
    )

    name = models.CharField(max_length=50, verbose_name="Nom (ex: Terminale)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Cycle")
    order = models.IntegerField(default=0, verbose_name="Ordre de tri", help_text="1 pour CP, 13 pour Terminale...")

    class Meta:
        ordering = ['order'] # Trie automatiquement du plus petit au plus grand
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Subject(models.Model):
    """
    Matière enseignée (ex: Maths, Piano, SVT).
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Matière")
    is_academic = models.BooleanField(default=True, verbose_name="Est-ce scolaire ?") # True = Maths, False = Piano/Cuisine

    class Meta:
        ordering = ['name']
        verbose_name = "Matière"
        verbose_name_plural = "Matières"

    def __str__(self):
        return self.name