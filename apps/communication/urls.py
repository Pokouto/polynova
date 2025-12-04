from django.urls import path
from . import views

urlpatterns = [
    path('nouveau/<int:user_id>/', views.start_thread, name='start_thread'),
    path('messagerie/', views.inbox, name='inbox'),
    path('messagerie/<int:pk>/', views.thread_detail, name='thread_detail'),
]