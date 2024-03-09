from django.shortcuts import render,redirect
from .models import *
from .forms import *
from django.contrib import messages

def Accueil(request):
    return render(request,"Accueil.html",{'navbar':'Accueil'})

def MarketData(request):
    return render(request,"MarketData.html",{'navbar':'MarketData'})

def add_cours(request):
    if request.method == "POST":
        form = Cours_revaluationForm(request.POST)
        form.save()
        messages.success(request,"Le cours du jour a été ajouté avec succès")
        return redirect('MarketData')

    return render(request,"MarketData.html",{'navbar':'MarketData'})

def add_bande(request):
    if request.method == "POST":
        form = Bande_fluctuationForm(request.POST)
        form.save()
        messages.success(request,"Le bande de fluctuation  a été ajouté avec succès.")
        return redirect('MarketData')

    return render(request,"MarketData.html",{'navbar':'MarketData'})
