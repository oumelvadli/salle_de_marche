import datetime
from datetime import datetime

from django.shortcuts import render,redirect
from .models import *
from .forms import *
from .forms import ExcelImportForm
from django.contrib import messages
import pandas as pd 
from django.db.models import Sum
from django.db.models import Q
import math 
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from decimal import Decimal
from django.core.paginator import Paginator
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.http import HttpResponse,JsonResponse
from openpyxl import Workbook



from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash

@login_required
def Accueil(request):
    return render(request,"Accueil.html",{'navbar':'Accueil'})

def EoD(request):
    return render(request,"EoD.html",{'navbar':'EoD'})

def MarketData(request):
    Cours_revaluations = Cours_revaluation.objects.all().order_by('-date')
    Bande_fluctuations = Bande_fluctuation.objects.all().order_by('-date')
    # date_actuelle = datetime.date.today().strftime('%Y-%m-%d')
    date_actuelle = datetime.now().date()

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

def convertir_en_decimal(valeur):
    return Decimal(str(valeur).replace(',', ''))
@login_required
def importer_donnees(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            fichier_excel = request.FILES['fichier_excel']
            data = pd.read_excel(fichier_excel, converters={'date_operation': lambda x: datetime.strptime(x, '%d/%m/%Y').date(),
                'date_validation': lambda x: datetime.strptime(x, '%d/%m/%Y').date(),'montant_vendu': convertir_en_decimal, 'montant_achat': convertir_en_decimal})
            imported_operations = 0  # Compteur d'opérations importées
                
            for index, row in data.iterrows():  
                     operation_exists = Operation.objects.filter(
                        Q(date_operation=row['date_operation']) &Q(date_validation=row['date_validation']) &Q(montant_vendu=row['montant_vendu']) &Q(conterpartie=row['conterpartie']) &Q(direction=row['direction']) & Q(devise_achat=row['devise_achat']) &Q(devise_vente=row['devise_vente']) &Q(cours=row['cours']) &Q(montant_achat=row['montant_achat']) &Q(type=row['type'])).exists()

                     if not operation_exists:
                        Operation.objects.create( date_operation=row['date_operation'],date_validation=row['date_validation'],conterpartie=row['conterpartie'],direction=row['direction'],devise_achat=row['devise_achat'],devise_vente=row['devise_vente'],cours=row['cours'], montant_achat=row['montant_achat'],montant_vendu=row['montant_vendu'],type=row['type']
                        )
                        imported_operations += 1
            # return JsonResponse({'success': True, 'nombre_lignes_importees': imported_operations})

            messages.success(request, f"{imported_operations} opérations ont été importées avec succès.")
                
               
    else:
        form = ExcelImportForm()
    return render(request, 'import.html', {'form': form})

@login_required
def visualisation(request):
    operations_list = Operation.objects.all()
    paginator =Paginator(operations_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'visualiser.html', {'page_obj': page_obj, 'navbar': 'visualisation'})
     
def add_operation(request):
    if request.method == "POST":
        form = OperationForm(request.POST)
        if form.is_valid():
            form.save()
            # messages.success(request,"L'operation  a été ajouté avec succès")
        return redirect('visualisation')
    else:
        form = OperationForm()
    return render(request, 'operation_form.html', {'form': form})


def update_operation(request, id):
    operation = Operation.objects.get(id=id)
    if request.method == 'POST':
        form = OperationForm(request.POST, instance=operation)
        if form.is_valid():
            form.save()
            return redirect('visualisation')
    else:
        form = OperationForm(instance=operation)
    return render(request, 'update_operation.html', {'form': form})

def delete_operation(request, id):
    operation = Operation.objects.get(id=id)
    if request.method == 'POST':
        operation.delete()
        return redirect('visualisation')  
    return render(request, 'delete_operation.html', {'operation': operation})
@login_required
def calcul_position(request):
    date_specifiee = request.GET.get('date_operation')
    if date_specifiee:
            date_specifiee = datetime.strptime(date_specifiee, '%d/%m/%Y').date()
    else:
        date_specifiee = datetime.now().date()

    operations = Operation.objects.filter(date_operation=date_specifiee)

    # Calcul du prix total d'achat et de vente pour chaque devise pour la date spécifiée
    prix_achat_total = operations.exclude(devise_achat='MRU').values('devise_achat').annotate(prix_achat_total=Sum(F('montant_achat')))
    prix_vente_total = operations.values('devise_vente').annotate(prix_vente_total=Sum(F('montant_vendu')))
    cv_achat = operations.values('devise_achat').annotate(cv_achat=Sum(F('montant_achat')*F('cours')))
    cv_vente = operations.values('devise_vente').annotate(cv_achat=Sum(F('montant_vendu')*F('cours')))
    print(cv_vente)
    print(cv_achat)


    
    # Calcul du prix moyen pondéré d'achat et de vente pour chaque devise pour la date spécifiée
    prix_moyen_achat = operations.values('devise_achat').annotate(
        prix_achat_total=Sum(F('montant_achat') * F('cours')),
        quantite_achat_total=Sum('montant_achat')
    ).annotate(prix_moyen_achat=ExpressionWrapper(F('prix_achat_total') / F('quantite_achat_total'), output_field=DecimalField()))

    prix_moyen_vente = operations.values('devise_vente').annotate(
        prix_vente_total=Sum(F('montant_vendu') * F('cours')),
        quantite_vente_total=Sum('montant_vendu')
    ).annotate(prix_moyen_vente=ExpressionWrapper(F('prix_vente_total') / F('quantite_vente_total'), output_field=DecimalField()))

    context = {
        'prix_achat_total': prix_achat_total,
        'prix_vente_total': prix_vente_total,
        'prix_moyen_achat': prix_moyen_achat,
        'prix_moyen_vente': prix_moyen_vente,
        'cv_achat': cv_achat,
        'cv_vente': cv_vente,
        'date_specifiee': date_specifiee,
    }
    return render(request, 'calcul.html', context)

def meilleures_contreparties(request):
    # Filtrer les opérations de vente pour les contreparties IB
    operations_sell_ib = Operation.objects.filter(direction='sell').filter(type='IB')
    ventes_par_contrepartie_ib = operations_sell_ib.values('conterpartie').annotate(total_ventes=Sum('montant_vendu'))
    ventes_par_contrepartie_ib = ventes_par_contrepartie_ib.order_by('-total_ventes')
    meilleures_contreparties_ib = ventes_par_contrepartie_ib[:5]

    # Filtrer les opérations de vente pour les contreparties CORP
    operations_sell_corp = Operation.objects.filter(direction='sell').filter(type='CORP')
    ventes_par_contrepartie_corp = operations_sell_corp.values('conterpartie').annotate(total_ventes=Sum('montant_vendu'))
    ventes_par_contrepartie_corp = ventes_par_contrepartie_corp.order_by('-total_ventes')
    meilleures_contreparties_corp = ventes_par_contrepartie_corp[:5]

    context = {
        'meilleures_contreparties_ib': meilleures_contreparties_ib,
        'meilleures_contreparties_corp': meilleures_contreparties_corp
    }
    return render(request, 'meilleures_contreparties.html', context)

def filter_operations(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    start_date = datetime.strptime(start_date, "%d/%m/%Y").strftime("%Y-%m-%d") if start_date else None
    end_date = datetime.strptime(end_date, "%d/%m/%Y").strftime("%Y-%m-%d") if end_date else None
    
    operations_list = Operation.objects.all()
    
    if start_date and end_date:
        operations_list = operations_list.filter(date_operation__range=[start_date, end_date])
    
    paginator = Paginator(operations_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'visualiser.html', {'page_obj': page_obj})


def export_to_excel(request):
    data = Operation.objects.all()
    wb = Workbook()
    ws = wb.active

    ws.append(['Date op', 'Date va', 'Conterpartie','Direction','Devise Achat','Devise vente','cours','Montant Achat','Montant vendu','Type'])


    for operation in data:
        ws.append([operation.date_operation, operation.date_validation,operation.conterpartie,operation.direction,operation.devise_achat,operation.devise_vente,operation.cours,operation.montant_achat,operation.montant_vendu,operation.type])
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="export.xlsx"'
    wb.save(response)
    return response


@staff_member_required
def gestion_utilisateurs(request):
    utilisateurs = User.objects.all()
    form=CustomUerCreationForm()
    return render(request, 'users.html', {'utilisateurs': utilisateurs,'form':form,'navbar': 'users'})

def inscription(request):
    if request.method == 'POST':
        form=CustomUerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre compte a été créé avec succès !')
            return redirect('users')
        else:
            # Form is not valid, render the form with errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return redirect('users')
    else:
        return redirect('users')

@staff_member_required
def toggle_user_active(request, user_id):
    user = User.objects.get( id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('users')

@staff_member_required
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect('users')

@staff_member_required
def change_password(request, user_id):
    user = User.objects.get( id=user_id)
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to update the session with the new password
            messages.success(request, 'Votre mot de passe a été modifié avec succès !')
            return redirect('users')
        else:
            messages.error(request, 'Une erreur s\'est produite lors de la modification de votre mot de passe.')
            return redirect('users')
    else:
        return redirect('users')
