from django.urls import path
from . import views

app_name = 'actualites'

urlpatterns = [
    path('', views.list_articles, name='list'),
    path('categorie/<slug:category_slug>/', views.list_articles, name='category'),
    
    # NOUVEAU : Détail et Like
    path('article/<slug:slug>/', views.article_detail, name='detail'),
    path('article/<slug:slug>/like/', views.like_article, name='like_article'),
]