"""
Django settings for config project.
Fichier de configuration PRINCIPAL de PolyNova.
"""

from pathlib import Path
import os
import sys
from django.utils.translation import gettext_lazy as _

# 1. Définition des chemins
BASE_DIR = Path(__file__).resolve().parent.parent

# Ajout du dossier 'apps' au chemin Python pour que Django trouve nos modules
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# 2. Sécurité
SECRET_KEY = 'django-insecure-remplace-moi-vite-en-prod-avec-une-cle-secrete'
DEBUG = True
ALLOWED_HOSTS = ['*']

# 3. Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Nos Applications (Modules)
    'apps.core',
    'apps.accounts',
    'apps.profiles',
    'apps.education',
    'apps.marketplace',
    'apps.billing',
    'apps.communication',
]

# 4. Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', # Indispensable pour le changement de langue
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# 5. Templates (HTML)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Dossier global des templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Notre processeur pour les notifications de messages
                'apps.communication.context_processors.unread_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# 6. Base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 7. Authentification Personnalisée
# C'EST ICI QUE L'ERREUR ÉTAIT : On met 'nom_app.Modele' sans le préfixe 'apps.'
AUTH_USER_MODEL = 'accounts.CustomUser'

# Redirections après connexion/déconnexion
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# 8. Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# 9. Internationalisation (I18N)
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('fr', _('Français')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# 10. Fichiers Statiques (CSS, JS, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# 11. Fichiers Média (Uploads utilisateurs)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuration ID par défaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'