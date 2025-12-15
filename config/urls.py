from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.conf.urls.i18n import i18n_patterns # <--- IMPORT IMPORTANT
from apps.core import admin_views
from apps.core import views as core_views

def home(request): return render(request, 'home.html')

# Ces URLs ne changent pas selon la langue (ex: le changement de langue lui-même)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# Ces URLs auront le préfixe /fr/ ou /en/
urlpatterns += i18n_patterns(
    # --- ADMIN DJANGO ---
    path('admin/', admin.site.urls),

    # --- PANEL ADMIN ---
    path('panel-admin/login/', admin_views.admin_login_view, name='admin_login'),
    path('panel-admin/logout/', admin_views.admin_logout, name='admin_logout'),
    path('panel-admin/', admin_views.custom_admin_dashboard, name='admin_dashboard'),
    
    # ... (Toutes vos autres routes ici : admin create, user update, etc.) ...
    # Copiez toutes les autres routes ici (Articles, Pays, etc.)
    path('panel-admin/admin/create/', admin_views.create_sub_admin, name='create_sub_admin'),
    path('panel-admin/admin/delete/<int:user_id>/', admin_views.delete_user, name='delete_sub_admin'),
    path('panel-admin/user/update/<int:user_id>/', admin_views.update_user_status, name='update_user_status'),
    path('panel-admin/user/delete/<int:user_id>/', admin_views.delete_user, name='delete_user'),
    path('panel-admin/tutor/validate/<int:profile_id>/', admin_views.validate_tutor, name='validate_tutor'),
    path('panel-admin/country/add/', admin_views.add_country, name='add_country'),
    path('panel-admin/country/config/<int:country_id>/', admin_views.update_country_config, name='update_country_config'),
    path('panel-admin/country/toggle/<int:country_id>/', admin_views.toggle_country, name='toggle_country'),
    path('panel-admin/country/delete/<int:country_id>/', admin_views.delete_country, name='delete_country'),
    path('panel-admin/request/delete/<int:request_id>/', admin_views.delete_request, name='delete_request'),
    path('panel-admin/article/create/', admin_views.create_article, name='create_article'),
    path('panel-admin/article/edit/<int:article_id>/', admin_views.edit_article, name='edit_article'),
    path('panel-admin/article/toggle/<int:article_id>/', admin_views.toggle_article_publish, name='toggle_article_publish'),
    path('panel-admin/article/delete/<int:article_id>/', admin_views.delete_article, name='delete_article'),
    path('panel-admin/category/create/', admin_views.create_category, name='create_category'),
    path('panel-admin/category/delete/<int:category_id>/', admin_views.delete_category, name='delete_category'),

    # --- PAGES PUBLIQUES ---
    path('a-propos/', core_views.about, name='about'),
    path('contact/', core_views.contact, name='contact'),
    path('faq/', core_views.faq, name='faq'),
    path('tarifs/', core_views.pricing, name='pricing'),

    # --- APPS ---
    path('compte/', include('apps.accounts.urls')),
    path('', include('apps.profiles.urls')),
    path('', include('apps.marketplace.urls')),
    path('', include('apps.billing.urls')),
    path('', include('apps.communication.urls')),
    path('blog/', include('apps.actualites.urls')),
    
    path('', home, name='home'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)