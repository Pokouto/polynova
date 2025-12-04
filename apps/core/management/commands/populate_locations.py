from django.core.management.base import BaseCommand
from apps.core.models import Country, City, Quartier

class Command(BaseCommand):
    help = 'Remplit la base de données avec les Pays, Villes et Communes du CDC'

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Démarrage de l'importation des données géographiques...")

        # 1. Création du PAYS : Côte d'Ivoire
        ci, created = Country.objects.get_or_create(
            code="CI",
            defaults={
                "name": "Côte d'Ivoire",
                "currency_symbol": "F CFA",
                "is_active": True,
                # Paramètres du CDC
                "min_budget_threshold": 30000,  # Seuil intention forte [cite: 382]
                "subscription_price": 3000      # Prix abonnement prof [cite: 497]
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Pays créé : {ci.name}"))
        else:
            self.stdout.write(f"ℹ️ Pays existant : {ci.name}")

        # 2. Création des VILLES Principales
        # Liste des villes citées ou implicites [cite: 342]
        villes_data = ["Abidjan", "Bouaké", "Yamoussoukro", "San-Pédro", "Daloa", "Korhogo"]
        
        ci_cities = {} # On garde en mémoire pour lier les quartiers après

        for nom_ville in villes_data:
            ville, v_created = City.objects.get_or_create(
                country=ci,
                name=nom_ville
            )
            ci_cities[nom_ville] = ville
            if v_created:
                self.stdout.write(f"  - Ville créée : {nom_ville}")

        # 3. Création des COMMUNES d'Abidjan (Selon le CDC) 
        abidjan = ci_cities["Abidjan"]
        
        communes_abidjan = [
            "Adjamé", 
            "Attécoubé", 
            "Cocody", 
            "Koumassi", 
            "Marcory", 
            "Plateau", 
            "Treichville", 
            "Yopougon", 
            "Abobo", 
            "Anyama", 
            "Bingerville"
        ]

        count_quartiers = 0
        for nom_commune in communes_abidjan:
            quartier, q_created = Quartier.objects.get_or_create(
                city=abidjan,
                name=nom_commune
            )
            if q_created:
                count_quartiers += 1

        self.stdout.write(self.style.SUCCESS(f"✅ {count_quartiers} Communes ajoutées à Abidjan."))
        self.stdout.write(self.style.SUCCESS("🎉 Terminé ! La base de données est prête pour les formulaires."))