from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_signalements, name='liste_signalements'),
]
