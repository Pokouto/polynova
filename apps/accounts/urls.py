from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Inscription
    path('inscription/', views.register, name='register'),
    
    # Connexion (Version Sécurisée Public Only)
    path('connexion/', views.public_login_view, name='login'),
    
    # Déconnexion (Standard)
    path('deconnexion/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]