"""
Django settings for config project.
Fichier de configuration PRINCIPAL de PolyNova.
"""

from pathlib import Path
import os
import sys
from django.utils.translation import gettext_lazy as _
import dj_database_url

# 1. Définition des chemins
BASE_DIR = Path(__file__).resolve().parent.parent

# Ajout du dossier 'apps' au chemin Python pour que Django trouve nos modules
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# 2. Sécurité - IMPORTANT POUR RENDER
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-remplace-moi-vite-en-prod-avec-une-cle-secrete')

# DEBUG sera True en local, False sur Render
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = []

# Ajouter automatiquement le hostname Render
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Pour développement local, autoriser localhost
if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])

# 3. Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',  # IMPORTANT pour Render

    # Nos Applications (Modules)
    'apps.core',
    'apps.accounts',
    'apps.profiles',
    'apps.education',
    'apps.marketplace',
    'apps.billing',
    'apps.communication',
    'apps.actualites',
]

# 4. Middleware - AJOUTER WhiteNoise
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # AJOUTER ICI
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

# 6. Base de données - CONFIGURATION POUR RENDER
# Utilise SQLite en local, PostgreSQL sur Render
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        conn_max_age=600
    )
}

# 7. Authentification Personnalisée
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

# 10. Fichiers Statiques (CSS, JS, Images) - CONFIGURATION POUR RENDER
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# IMPORTANT pour Render: dossier où collectstatic va mettre les fichiers
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuration WhiteNoise pour servir les fichiers statiques
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 11. Fichiers Média (Uploads utilisateurs)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuration ID par défaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 12. Configuration supplémentaire pour Render
if not DEBUG:
    # Sécurité HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Cache des fichiers statiques
    WHITENOISE_MAX_AGE = 31536000  # 1 an en secondes
    
    # Logging pour Render
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }