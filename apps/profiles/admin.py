from django.contrib import admin
from .models import TutorProfile, ParentProfile

@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    # Ce qu'on voit dans la liste des profs
    list_display = ('user', 'status', 'is_visible', 'created_at')
    
    # Les filtres sur la droite
    list_filter = ('status', 'is_home_class', 'is_online_class', 'created_at')
    
    # Barre de recherche (Chercher par nom ou email)
    search_fields = ('user__username', 'user__email', 'user__phone')
    
    # Actions rapides (Valider plusieurs profs d'un coup)
    actions = ['approve_profiles', 'reject_profiles']

    # Fonction personnalisée pour afficher une icône vert/rouge
    @admin.display(boolean=True, description='Visible ?')
    def is_visible(self, obj):
        return obj.is_visible()

    # Action : Tout valider
    def approve_profiles(self, request, queryset):
        queryset.update(status='validated')
    approve_profiles.short_description = "✅ Valider les dossiers sélectionnés"

    # Action : Tout rejeter
    def reject_profiles(self, request, queryset):
        queryset.update(status='rejected')
    reject_profiles.short_description = "❌ Rejeter les dossiers sélectionnés"

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_phone_verified', 'address')
    list_filter = ('is_phone_verified',)
    search_fields = ('user__username', 'user__email')