import datetime
from django.shortcuts import render,redirect
from .models import *
from .forms import *
from .forms import ExcelImportForm
from django.contrib import messages
import pandas as pd 


def Accueil(request):
    return render(request,"Accueil.html",{'navbar':'Accueil'})

def MarketData(request):
    Cours_revaluations = Cours_revaluation.objects.all()
    Bande_fluctuations = Bande_fluctuation.objects.all()
    date_actuelle = datetime.date.today().strftime('%Y-%m-%d')
    return render(request,"MarketData.html",{'navbar':'MarketData','date_actuelle':date_actuelle,'Cours_revaluations':Cours_revaluations,'Bande_fluctuations':Bande_fluctuations})

def Traitment(request):
    return render(request,"traitment.html",{'navbar':'Traitement'})

def add_cours(request):
    if request.method == "POST":
        form = Cours_revaluationForm(request.POST)
        form.save()
        messages.success(request,"Le cours du jour a été ajouté avec succès")
        return redirect('MarketData')
    return render(request,"MarketData.html",{'navbar':'MarketData'})

def edit_cours(request, id):
    cours = Cours_revaluation.objects.get(id=id)
    return render(request,'materiels/edit.html',{'navbar':'MarketData','cours':cours})
def update_cours(request, id):
    cours = Cours_revaluation.objects.get(id=id)
    form = Cours_revaluationForm(request.POST, instance=cours)
    form.save()
    return redirect('MarketData')

def add_bande(request):
    if request.method == "POST":
        form = Bande_fluctuationForm(request.POST)
        form.save()
        messages.success(request,"Le bande de fluctuation  a été ajouté avec succès.")
        return redirect('MarketData')

    return render(request,"MarketData.html",{'navbar':'MarketData'})

# def edit_bande(request, id):
#     bande = Bande_fluctuation.objects.get(id=id)
#     return render(request,'materiels/edit.html',{'navbar':'MarketData','bande':bande})
# def update_bande(request, id):
#     bande = Bande_fluctuation.objects.get(id=id)
#     form = Bande_fluctuationForm(request.POST, instance=bande)
#     form.save()
#     return redirect('MarketData')



def importer_donnees(request):
    
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            fichier_excel = request.FILES['fichier_excel']
            if fichier_excel.name.endswith('.xlsx'):
                data = pd.read_excel(fichier_excel)
                for index, row in data.iterrows():
                    Operation.objects.create(date_operation=row['date_operation'],date_validation=row['date_validation'],conterpartie=row['conterpartie'],devise_achat=row['devise_achat'],devise_vente=row['devise_vente'],cours=row['cours'],montant_achat=row['montant_achat'],type=row['type'])
                messages.success(request,'le fichier est importé avec succès')
            else:
                # Fichier non pris en charge
                messages.error(request, 'Le fichier doit être au format Excel (.xlsx)')
    else:
        form = ExcelImportForm()
    return render(request, 'import.html', {'form': form})



def visualisation(request):
    operations = Operation.objects.all()
    return render(request, 'visualiser.html', {'operations': operations})