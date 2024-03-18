from django.shortcuts import render,redirect
from .models import *
from .forms import *
from .forms import ExcelImportForm
from django.contrib import messages
import pandas as pd 
from datetime import datetime

def Accueil(request):
    return render(request,"Accueil.html",{'navbar':'Accueil'})

def MarketData(request):
    return render(request,"MarketData.html",{'navbar':'MarketData'})

def Traitment(request):
    return render(request,"traitment.html",{'navbar':'Traitement'})

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


def importer_donnees(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            fichier_excel = request.FILES['fichier_excel']
            if fichier_excel.name.endswith('.xlsx'):
                data = pd.read_excel(fichier_excel)
                imported_operations = 0  # Compteur d'opérations importées

                for index, row in data.iterrows():
                    operation_exists = Operation.objects.filter(
                        Q(date_operation=row['date_operation']) &Q(date_validation=row['date_validation']) &Q(conterpartie=row['conterpartie']) & Q(devise_achat=row['devise_achat']) &Q(devise_vente=row['devise_vente']) &Q(cours=row['cours']) &Q(montant_achat=row['montant_achat']) &Q(type=row['type'])).exists()

                    if not operation_exists:

                        Operation.objects.create( date_operation=row['date_operation'],date_validation=row['date_validation'],conterpartie=row['conterpartie'],devise_achat=row['devise_achat'],devise_vente=row['devise_vente'],cours=row['cours'], montant_achat=row['montant_achat'],type=row['type']
                        )
                        imported_operations += 1

                messages.success(request, f"{imported_operations} opérations ont été importées avec succès.")
            else:
                # Fichier non pris en charge
                messages.error(request, 'Le fichier doit être au format Excel (.xlsx)')
    else:
        form = ExcelImportForm()
    return render(request, 'import.html', {'form': form})

def visualisation(request):
    operations = Operation.objects.all()
    return render(request, 'visualiser.html', {'operations': operations})
from django.db.models import Q



from .forms import DateFilterForm

def filtrer(request):
    form = DateFilterForm(request.GET)
    operations = Operation.objects.all()

    if form.is_valid():
        date_operation = form.cleaned_data['date']
        if date_operation:
            operations = Operation.objects.filter(date_operation=date_operation)

    return render(request, 'visualiser.html', {'operations': operations, 'form': form})
