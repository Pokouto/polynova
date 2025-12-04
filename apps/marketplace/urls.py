from django.urls import path
from . import views

urlpatterns = [
    # Côté Parent
    path('demande/nouvelle/', views.create_request, name='create_request'),
    path('demande/modifier/<int:pk>/', views.edit_request, name='edit_request'),
    
    # Côté Prof (Place de marché)
    path('espace-enseignant/demandes/', views.request_list, name='request_list'),
    
    # Public
    path('annuaire/', views.tutor_list, name='tutor_list'),
    path('professeur/<int:pk>/', views.tutor_detail, name='tutor_detail'),
]