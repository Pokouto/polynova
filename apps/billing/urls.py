from django.urls import path
from . import views

urlpatterns = [
    path('paiement-test/<int:tutor_id>/', views.fake_payment, name='fake_payment'),
]