import datetime
from django.shortcuts import render,redirect
from .models import *
from .forms import *
from .forms import ExcelImportForm
from django.contrib import messages
import pandas as pd 
from datetime import datetime
from django.db.models import Q


def Accueil(request):
    return render(request,"Accueil.html",{'navbar':'Accueil'})

def MarketData(request):
    Cours_revaluations = Cours_revaluation.objects.all().order_by('-date')
    Bande_fluctuations = Bande_fluctuation.objects.all().order_by('-date')
    date_actuelle = datetime.date.today().strftime('%Y-%m-%d')
    return render(request,"MarketData.html",{'navbar':'MarketData','date_actuelle':date_actuelle,'Cours_revaluations':Cours_revaluations,'Bande_fluctuations':Bande_fluctuations})

def Traitment(request):
    return render(request,"traitment.html",{'navbar':'Traitement'})

def add_cours(request):
    if request.method == "POST":
        form = Cours_revaluationForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            if Cours_revaluation.objects.filter(date=date).exists():
                messages.error(request, 'Cette date existe déjà. Veuillez saisir une autre date.')
            else:
                form.save()
                messages.success(request,"Le cours du jour a été ajouté avec succès")
        return redirect('MarketData')
    return render(request,"MarketData.html",{'navbar':'MarketData'})


def update_cours(request, id):
    cours = Cours_revaluation.objects.get(id=id)
    form = Cours_revaluationForm(request.POST, instance=cours)
    if form.is_valid():
            date = form.cleaned_data['date']
            if Cours_revaluation.objects.filter(date=date).exists():
                messages.error(request, 'Cette date existe déjà. Veuillez saisir une autre date.')
            else:
                form.save()
                messages.success(request,"Le cours du jour a été ajouté avec succès")
    
    return redirect('MarketData')

def add_bande(request):
    if request.method == "POST":
        form = Bande_fluctuationForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            if Bande_fluctuation.objects.filter(date=date).exists():
                messages.error(request, 'Cette date existe déjà. Veuillez saisir une autre date.')
            else:
                form.save()
                messages.success(request, 'La Bande de fluctuation a été ajouté avec succès.')
        return redirect('MarketData')

    return render(request,"MarketData.html",{'navbar':'MarketData'})


def update_bande(request, id):
    bande = Bande_fluctuation.objects.get(id=id)
    form = Bande_fluctuationForm(request.POST, instance=bande)
    if form.is_valid():
        date = form.cleaned_data['date']
        if Bande_fluctuation.objects.filter(date=date).exists():
            messages.error(request, 'Cette date existe déjà. Veuillez saisir une autre date.')
        else:
            form.save()
            messages.success(request, 'La Bande de fluctuation a été ajouté avec succès.')
    return redirect('MarketData')



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
    return render(request, 'visualiser.html', {'operations': operations,'navbar':'visualisation'})
