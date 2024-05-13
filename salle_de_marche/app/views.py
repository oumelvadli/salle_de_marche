import datetime
from datetime import datetime,timedelta

from django.utils import timezone
from django.shortcuts import render,redirect
from .models import *
from .forms import *
from .forms import ExcelImportForm
from django.contrib import messages
import pandas as pd 
from django.db.models import Sum
from django.db.models import Q
import math 
import json
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from decimal import Decimal
from django.core.paginator import Paginator
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.http import HttpResponse,JsonResponse
from openpyxl import Workbook
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.http import JsonResponse




from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from xhtml2pdf import pisa
from django.template import loader
from django.shortcuts import get_object_or_404


@login_required
def Accueil(request):
    # Appeler la tâche Celery pour traiter les alertes
    session_status = SessionStatus.objects.first()
    # Alert(request)
    return render(request, "Accueil.html", {'navbar': 'Accueil','session_status': session_status})

def EoD(request):
    return render(request,"EoD.html",{'navbar':'EoD'})

def MarketData(request):
    Cours_revaluations = Cours_revaluation.objects.all().order_by('-date')
    Bande_fluctuations = Bande_fluctuation.objects.all().order_by('-date')
    # date_actuelle = datetime.date.today().strftime('%Y-%m-%d')
    date_actuelle = datetime.now().date()
    session_status = SessionStatus.objects.first()
    return render(request,"MarketData.html",{'navbar':'MarketData','date_actuelle':date_actuelle,'Cours_revaluations':Cours_revaluations,'Bande_fluctuations':Bande_fluctuations,'session_status': session_status})

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
            if Cours_revaluation.objects.exclude(id=id).filter(date=date).exists():
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
        if Bande_fluctuation.objects.exclude(id=id).filter(date=date).exists():
            messages.error(request, 'Cette date existe déjà. Veuillez saisir une autre date.')
        else:
            form.save()
            messages.success(request, 'La Bande de fluctuation a été ajouté avec succès.')
    return redirect('MarketData')

def convertir_en_decimal(valeur):
    return Decimal(str(valeur).replace(',', ''))
@login_required
def importer_donnees(request):
    session_status = SessionStatus.objects.first()
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            fichier_excel = request.FILES['fichier_excel']
            if fichier_excel.name.endswith('.xlsx'):
                try:
                    data = pd.read_excel(fichier_excel, converters={'montant_vendu': convertir_en_decimal, 'montant_achat': convertir_en_decimal})
                    imported_operations = 0  # Compteur d'opérations importées

                    for index, row in data.iterrows():
                        # Vérifier si toutes les colonnes nécessaires sont présentes dans la ligne
                        required_columns = ['date_operation', 'date_validation', 'montant_vendu', 'conterpartie', 'direction', 'devise_achat', 'devise_vente', 'cours', 'montant_achat', 'type']
                        missing_columns = [col for col in required_columns if col not in row.index]

                        if missing_columns:
                            # Générer un message d'erreur indiquant les colonnes manquantes
                            error_message = f"Les colonnes suivantes sont manquantes dans la ligne {index+1}: {', '.join(missing_columns)}"
                            messages.error(request, error_message)
                            return render(request, 'import.html', {'form': form})

                        # Vérifier si une cellule est vide
                        empty_cells = [col for col, value in row.items() if pd.isnull(value)]

                        if empty_cells:
                            # Générer un message d'erreur indiquant les cellules vides
                            error_message = f"Les cellules suivantes sont vides dans la ligne {index+1}: {', '.join(empty_cells)}"
                            messages.error(request, error_message)
                            return render(request, 'import.html', {'form': form})

                        operation_exists = Operation.objects.filter(
                            Q(date_operation=row['date_operation']) & Q(date_validation=row['date_validation']) & Q(montant_vendu=row['montant_vendu']) & Q(conterpartie=row['conterpartie']) & Q(direction=row['direction']) & Q(devise_achat=row['devise_achat']) & Q(devise_vente=row['devise_vente']) & Q(cours=row['cours']) & Q(montant_achat=row['montant_achat']) & Q(type=row['type'])).exists()

                        if not operation_exists:
                            Operation.objects.create(date_operation=row['date_operation'], date_validation=row['date_validation'], conterpartie=row['conterpartie'], direction=row['direction'], devise_achat=row['devise_achat'], devise_vente=row['devise_vente'], cours=row['cours'], montant_achat=row['montant_achat'], montant_vendu=row['montant_vendu'], type=row['type'])
                            imported_operations += 1

                    messages.success(request, f"{imported_operations} opérations ont été importées avec succès.")
                except Exception as e:
                    # Gérer les exceptions lors de la lecture du fichier Excel
                    messages.error(request, f"Une erreur s'est produite lors de l'importation du fichier Excel: {str(e)}")
            else:
                # Fichier non pris en charge
                messages.error(request, 'Le fichier doit être au format Excel (.xlsx)')
               
    else:
        form = ExcelImportForm()
    return render(request, 'import.html', {'form': form,'navbar': 'importer','session_status': session_status})


from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear

@login_required
def visualisation(request):
    # operations_list = Operation.objects.all()
    session_status = SessionStatus.objects.first()
    operations_list = Operation.objects.all().order_by(
        ExtractYear('date_operation').desc(),
        ExtractMonth('date_operation').desc(),
        ExtractDay('date_operation').desc()
    )
    paginator =Paginator(operations_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'visualiser.html', {'page_obj': page_obj, 'navbar': 'visualisation','session_status': session_status})
     
def add_operation(request):
    if request.method == "POST":
        form = OperationForm(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            # messages.success(request,"L'operation  a été ajouté avec succès")
        return redirect('visualisation')
    else:
        form = OperationForm()
    return render(request, 'visualiser.html', {'form': form})


def update_operation(request, id):
    operation = Operation.objects.get(id=id)
    if request.method == 'POST':
        form = OperationForm(request.POST, instance=operation)
        if form.is_valid():
            form.save()
            return redirect('visualisation')


def delete_operation(request, id):
    operation = Operation.objects.get(id=id)
    if request.method == 'POST':
        operation.delete()
        return redirect('visualisation')  
    return render(request, 'delete_operation.html', {'operation': operation})
from django.db.models.functions import Coalesce

@login_required
def calcul_position(request):
    date_specifiee = request.GET.get('date_operation')
    session_status = SessionStatus.objects.first()
    if date_specifiee:
        date_specifiee = datetime.strptime(date_specifiee, '%d/%m/%Y').date()
    else:
        date_specifiee = datetime.now().date()
    date_finale = date_specifiee + timedelta(days=1)

    
    # Opérations sur 24 heures
    operations = Operation.objects.filter(date_operation__gte=date_specifiee, date_operation__lt=date_finale)
    operations = Operation.objects.filter(date_operation=date_specifiee)

    prix_achat_total = operations.exclude(devise_achat='MRU').values('devise_achat').annotate(
        prix_achat_total=Sum(F('montant_achat')),
        quantite_achat_total=Sum('montant_achat'),
        cv_achat=Sum(F('montant_achat') * F('cours'))
    ).annotate(
        prix_moyen_achat=ExpressionWrapper(F('cv_achat') / F('quantite_achat_total'), output_field=DecimalField())
    )

    prix_vente_total = operations.values('devise_vente').annotate(
        prix_vente_total=Sum(F('montant_vendu')),
        quantite_vente_total=Sum('montant_vendu'),
        cv_vente=Sum(F('montant_vendu') * F('cours'))
    ).annotate(
        prix_moyen_vente=ExpressionWrapper(F('cv_vente') / F('quantite_vente_total'), output_field=DecimalField())
    )


    context = {
        'prix_achat_total': prix_achat_total,
        'prix_vente_total': prix_vente_total,
        'date_specifiee': date_specifiee,
        'navbar': 'calcul',
        'session_status': session_status
    }
    return render(request, 'calcul.html', context)

def meilleures_contreparties(request):
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
        'meilleures_contreparties_corp': meilleures_contreparties_corp,
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


def export_to_excel_operations(request):
    data = Operation.objects.all()
    wb = Workbook()
    ws = wb.active

    ws.append(['Date op', 'Date va', 'Conterpartie','Direction','Devise Achat','Devise vente','cours','Montant Achat','Montant vendu','Type'])


    for operation in data:
        ws.append([operation.date_operation, operation.date_validation,operation.conterpartie,operation.direction,operation.devise_achat,operation.devise_vente,operation.cours,operation.montant_achat,operation.montant_vendu,operation.type])
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Operations.xlsx"'
    wb.save(response)
    return response

def export_to_excel_reporting(request):
    if request.method == 'POST':
        table_data = json.loads(request.POST.get('tableData'))

        wb = Workbook()
        ws = wb.active

        for row_data in table_data:
            ws.append(row_data)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Reporting.xlsx'

        wb.save(response)
        return response


@staff_member_required
def gestion_utilisateurs(request):
    utilisateurs = User.objects.all()
    session_status = SessionStatus.objects.first()
    form=CustomUerCreationForm()
    return render(request, 'users.html', {'utilisateurs': utilisateurs,'form':form,'navbar': 'users','session_status': session_status})

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


def download_ticket(request, operation_id):
    operation = get_object_or_404(Operation, id=operation_id)

    # Chargez le template à l'aide du moteur de template
    template = loader.get_template('tickete.html')

    # Créez un dictionnaire avec les données de l'opération pour le contexte
    context = {'operation': operation}

    # Rendez les données dans le template en utilisant le contexte
    rendered_template = template.render(context, request)

    # Utilisez xhtml2pdf pour générer le PDF à partir du contenu rendu
    pdf_output = pisa.CreatePDF(rendered_template)

    if not pdf_output.err:
        # Créez une réponse HttpResponse avec le contenu PDF généré
        response = HttpResponse(pdf_output.dest.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'filename="tickete.pdf"'  # Nom du fichier de téléchargement
        return response
    else:
        return HttpResponse('Erreur lors de la génération du PDF.', status=500)
    
    
    
def update_session(request):
    session_status = SessionStatus.objects.first()
    if request.method == 'POST':
        is_open=request.POST.get('is_open')
        is_open = is_open.lower() == 'true'
        session_status.is_open=is_open
        session_status.start_jour=request.POST.get('start_jour')
        session_status.start_time=request.POST.get('start_time')
        session_status.end_jour=request.POST.get('end_jour')
        session_status.end_time=request.POST.get('end_time')
        session_status.save()
        return redirect("Accueil")
    return HttpResponse("Une erreure s'est produite lors de l'operation")

    
from .consumers import AlertConsumer

SEUIL_VENTE_MAXIMAL_PAR_CONTREPARTIE = 100000  # Seuil de vente maximal par contrepartie

# def limit():
#     # Récupérer la date d'il y a 48 heures
#     start_date = timezone.now() - timezone.timedelta(days=2)

#     # Obtenir la liste des contreparties distinctes ayant des opérations de vente récentes
#     distinct_counterparties = Operation.objects.filter(
#         date_operation__gte=start_date,
#         direction='Sell'  # Filtrer uniquement les ventes
#     ).values_list('conterpartie', flat=True).distinct()

#     # Pour chaque contrepartie, vérifier si le total vendu dépasse le seuil maximal
#     alerts = {}
#     for conterpartie in distinct_counterparties:
#         total_sold = Operation.objects.filter(
#             date_operation__gte=start_date,
#             direction='Sell',  # Filtrer uniquement les ventes
#             conterpartie=conterpartie  # Filtrer par contrepartie
#         ).aggregate(total_sold=Sum('montant_vendu'))['total_sold'] or 0

#         print(f"Total vendu pour {conterpartie} :", total_sold)

#         alert = total_sold >= max(SEUIL_VENTE_MAXIMAL_PAR_CONTREPARTIE, 0)
#         alerts[conterpartie] = (alert, total_sold)

#     return alerts








# def Alert(request):
#     # Récupérer la date d'il y a 48 heures
#     start_date = timezone.now() - timezone.timedelta(days=2)

#     # Obtenir la liste des contreparties distinctes ayant des opérations de vente récentes
#     distinct_counterparties = Operation.objects.filter(
#         date_operation__gte=start_date,
#         direction='Sell'  # Filtrer uniquement les ventes
#     ).values_list('conterpartie', flat=True).distinct()

#     # Initialisation des variables
#     showAlert = False
#     alertMessages = {}

#     # Pour chaque contrepartie, vérifier si le total vendu dépasse le seuil maximal
#     for contrepartie in distinct_counterparties:
#         total_sold = Operation.objects.filter(
#             date_operation__gte=start_date,
#             direction='Sell',  # Filtrer uniquement les ventes
#             conterpartie=contrepartie  # Filtrer par contrepartie
#         ).aggregate(total_sold=Sum('montant_vendu'))['total_sold'] or 0

#         print(f"Total vendu pour {contrepartie} :", total_sold)

#         alert = total_sold >= max(SEUIL_VENTE_MAXIMAL_PAR_CONTREPARTIE, 0)
#         if alert:
#             showAlert = True
#             alertMessages[contrepartie] = f"Alerte pour {contrepartie} : Vous êtes sur le point d'atteindre votre limite maximale de vente. Le total vendu est de {total_sold}."

#             # Envoi du message via le canal WebSocket
#             channel_layer = get_channel_layer()
#             async_to_sync(channel_layer.group_send)(
#                 'alert_group',  # Nom du groupe WebSocket
#                 {
#                     'type': 'alert_message',  # Nom de la méthode du consommateur
#                     'message': alertMessages[contrepartie]  # Contenu du message
#                 }
#             )

#     # Retourne la réponse JSON
#     return JsonResponse({
#         'showAlert': showAlert,
#         'alertMessages': alertMessages
#     })



































# Importations Django
from django.http import JsonResponse
from django.views.generic import View
from django.conf import settings

# Importation de la bibliothèque requests
import requests

# Vue pour récupérer les données boursièr
def get(request):
        # Récupération du symbole de l'action à partir des paramètres de requête
        symbol = request.GET.get('symbol', None)
        if not symbol:
            return JsonResponse({'error': 'Veuillez fournir un symbole d\'action'})

        # Construction de l'URL de l'API IEX Cloud
        url = f'https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={settings.IEX_CLOUD_API_KEY}'

        # Effectuer la requête HTTP GET
        response = requests.get(url)
        if response.status_code != 200:
            return JsonResponse({'error': 'Impossible de récupérer les données boursières'})

        # Convertir la réponse JSON en dictionnaire Python
        data = response.json()

        # Retourner les données boursières en tant que réponse JSON
        return JsonResponse(data)
























from .tasks import op

def test_task(request):
    result=1
    for i in range(5):
        Test.objects.create(
            nom=f"mariem {i}",
            prenom="mohamed",
            
           
        )
      
        result="done"
    return render(request,'task.html',{'result':result})



# def test_recup(request,task_id):
#     result=add.AsyncResult(task_id)
#     if result.ready():
#         return render(request,'recup.html',{'result':result.result})
#     return render(request,'recup.html',{'result':"result not ready yet"})





