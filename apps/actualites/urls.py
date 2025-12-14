from django.urls import path
from . import views

app_name = 'actualites'
urlpatterns = [
    path('', views.list_articles, name='list'),
    path('categorie/<slug:category_slug>/', views.list_articles, name='category'),
]