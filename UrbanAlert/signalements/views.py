from django.shortcuts import render
from .models import Signalement

def liste_signalements(request):
    signalements = Signalement.objects.all()
    return render(request, 'signalements/liste.html', {'signalements': signalements})

# Create your views here.
