from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from apps.core import admin_views

# Vue simple pour l'accueil
def home(request):
    return render(request, 'home.html')

urlpatterns = [
    # Admin Django natif (Base de données brute)
    path('admin/', admin.site.urls),
    
    # --- ROUTE POUR CHANGER DE LANGUE ---
    path('i18n/', include('django.conf.urls.i18n')), 
    
    # --- PANEL ADMIN PERSONNALISÉ ---
    path('panel-admin/', admin_views.custom_admin_dashboard, name='admin_dashboard'),
    path('panel-admin/login/', admin_views.admin_login_view, name='admin_login'),
    path('panel-admin/logout/', admin_views.admin_logout, name='admin_logout'),
    
    # Gestion Utilisateurs (Création Admin / Suppression)
    path('panel-admin/create-admin/', admin_views.create_sub_admin, name='create_sub_admin'),
    path('panel-admin/delete-user/<int:user_id>/', admin_views.delete_user, name='delete_user'),
    
    # Gestion Pays (Admin)
    path('panel-admin/country/add/', admin_views.add_country, name='add_country'),
    path('panel-admin/country/toggle/<int:country_id>/', admin_views.toggle_country, name='toggle_country'),
    path('panel-admin/country/delete/<int:country_id>/', admin_views.delete_country, name='delete_country'),

    # Gestion Demandes (Admin)
    path('panel-admin/request/delete/<int:request_id>/', admin_views.delete_request, name='delete_request'),

    # --- NOS APPLICATIONS ---
    path('compte/', include('apps.accounts.urls')),      # Auth (Login/Register public)
    path('', include('apps.profiles.urls')),             # Profils & Dashboard
    path('', include('apps.marketplace.urls')),          # Annuaire & Demandes
    path('', include('apps.billing.urls')),              # Paiements
    path('', include('apps.communication.urls')),        # Messagerie interne
    
    # Page d'accueil (Route racine)
    path('', home, name='home'),
]

# Gestion des fichiers médias (Images, PDF) en mode DÉVELOPPEMENT
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)