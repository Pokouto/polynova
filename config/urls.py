from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from apps.core import admin_views
from apps.core import views as core_views

# Vue simple pour l'accueil
def home(request):
    return render(request, 'home.html')

urlpatterns = [
    # --- 1. ADMIN DJANGO (Technique) ---
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')), 

    # --- 2. PANEL ADMIN (Back-Office) ---
    # Auth
    path('panel-admin/login/', admin_views.admin_login_view, name='admin_login'),
    path('panel-admin/logout/', admin_views.admin_logout, name='admin_logout'),
    path('panel-admin/', admin_views.custom_admin_dashboard, name='admin_dashboard'),

    # Gestion des Admins
    path('panel-admin/admin/create/', admin_views.create_sub_admin, name='create_sub_admin'),
    path('panel-admin/admin/delete/<int:user_id>/', admin_views.delete_user, name='delete_sub_admin'),

    # Gestion des Utilisateurs (Parents & Profs)
    path('panel-admin/user/update/<int:user_id>/', admin_views.update_user_status, name='update_user_status'),
    path('panel-admin/user/delete/<int:user_id>/', admin_views.delete_user, name='delete_user'),
    
    # Gestion Validation Professeurs
    path('panel-admin/tutor/validate/<int:profile_id>/', admin_views.validate_tutor, name='validate_tutor'),

    # Gestion Pays & Configuration
    path('panel-admin/country/add/', admin_views.add_country, name='add_country'),
    path('panel-admin/country/config/<int:country_id>/', admin_views.update_country_config, name='update_country_config'),
    path('panel-admin/country/toggle/<int:country_id>/', admin_views.toggle_country, name='toggle_country'),
    path('panel-admin/country/delete/<int:country_id>/', admin_views.delete_country, name='delete_country'),

    # Gestion Demandes
    path('panel-admin/request/delete/<int:request_id>/', admin_views.delete_request, name='delete_request'),

    # --- 3. GESTION BLOG (Panel Admin) ---
    path('panel-admin/article/create/', admin_views.create_article, name='create_article'),
    path('panel-admin/article/edit/<int:article_id>/', admin_views.edit_article, name='edit_article'),
    path('panel-admin/article/toggle/<int:article_id>/', admin_views.toggle_article_publish, name='toggle_article_publish'),
    path('panel-admin/article/delete/<int:article_id>/', admin_views.delete_article, name='delete_article'),

    # --- 4. PAGES PUBLIQUES ---
    path('a-propos/', core_views.about, name='about'),
    path('contact/', core_views.contact, name='contact'),
    path('faq/', core_views.faq, name='faq'),
    path('tarifs/', core_views.pricing, name='pricing'),

    # --- 5. APPLICATIONS MÉTIER ---
    path('compte/', include('apps.accounts.urls')),
    path('', include('apps.profiles.urls')),
    path('', include('apps.marketplace.urls')),
    path('', include('apps.billing.urls')),
    path('', include('apps.communication.urls')),
    
    # Le Blog Public
    path('blog/', include('apps.actualites.urls')),
    
    # --- 6. ACCUEIL ---
    path('', home, name='home'),
]

# Gestion des fichiers médias (Images)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)