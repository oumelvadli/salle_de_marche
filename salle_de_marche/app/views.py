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
import ftplib
from django.http import HttpResponse
import tempfile
import os



from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from xhtml2pdf import pisa
from django.template import loader
from django.shortcuts import get_object_or_404




@login_required
def Accueil(request):
    cours_eur = Cours_revaluation.objects.filter(devise='EUR').order_by('date')
    cours_dates_eur = [cours.date.strftime('%Y-%m-%d') for cours in cours_eur]
    cours_values_eur = [cours.cours for cours in cours_eur]
    cours_dates_eur_json = json.dumps(cours_dates_eur)
    cours_values_eur_json = json.dumps(cours_values_eur)

    cours_usd = Cours_revaluation.objects.filter(devise='USD').order_by('date')
    cours_dates_usd = [cours.date.strftime('%Y-%m-%d') for cours in cours_usd]
    cours_values_usd = [cours.cours for cours in cours_usd]
    cours_dates_usd_json = json.dumps(cours_dates_usd)
    cours_values_usd_json = json.dumps(cours_values_usd)

    date_actuelle = timezone.now().strftime('%Y-%m-%dT%H:%M:%S')  # Date actuelle au format ISO8601
    session_status = SessionStatus.objects.first()

    return render(request, "Accueil.html", {
        'navbar': 'Accueil',
        'date_actuelle': date_actuelle,
        'cours_dates_eur': cours_dates_eur_json,
        'cours_values_eur': cours_values_eur_json,
        'cours_dates_usd': cours_dates_usd_json,
        'cours_values_usd': cours_values_usd_json,
        'session_status': session_status
    })



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
            devise = form.cleaned_data['devise']
            if Cours_revaluation.objects.filter(date=date,devise=devise).exists():
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
            devise = form.cleaned_data['devise']
            if Cours_revaluation.objects.exclude(id=id).filter(date=date,devise=devise).exists():
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
    operations_list = Operation.objects.filter(type='IB').order_by(
        ExtractYear('date_operation').desc(),
        ExtractMonth('date_operation').desc(),
        ExtractDay('date_operation').desc()
    )

    return render(request, 'visualiser.html', {'page_obj': operations_list, 'navbar': 'visualisation','session_status': session_status})

@login_required
def visualisationCorp(request):
    # operations_list = Operation.objects.all()
    session_status = SessionStatus.objects.first()
    operations_list = OperationCorp.objects.all().order_by(
        ExtractYear('datoper').desc(),
        ExtractMonth('datoper').desc(),
        ExtractDay('datoper').desc()
    )

    return render(request, 'operationscorp.html', {'page_obj': operations_list, 'navbar': 'visualisation','session_status': session_status})
     
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
    
    
    return render(request, 'visualiser.html', {'page_obj': operations_list})
def filter_operationscorp(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    start_date = datetime.strptime(start_date, "%d/%m/%Y").strftime("%Y-%m-%d") if start_date else None
    end_date = datetime.strptime(end_date, "%d/%m/%Y").strftime("%Y-%m-%d") if end_date else None
    
    operations_list = OperationCorp.objects.all()
    
    if start_date and end_date:
        operations_list = operations_list.filter(datoper__range=[start_date, end_date])
    

    
    return render(request, 'operationscorp.html', {'page_obj': operations_list})


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


# class Position(models.Model):
#     date = models.DateField()
#     devise = models.CharField(max_length=10)
#     montant_initial = models.DecimalField(max_digits=10, decimal_places=2)
#     montant_final = models.DecimalField(max_digits=10, decimal_places=2, null=True)

#     def __str__(self):
#         return f"{self.date} | {self.devise} | Initial: {self.montant_initial}, Final: {self.montant_final}"




def last_business_day():
    today = datetime.date.today()
    shift = datetime.timedelta(max(1, (today.weekday() + 6) % 7 - 3))
    last_business_day = today - shift
    return last_business_day

def list_ftp_files(request):
    ftp_server = os.getenv('FTP_SERVER', '10.158.120.210')
    username = os.getenv('FTP_USERNAME', 'Moustapha')
    password = os.getenv('FTP_PASSWORD', 'Admin@CDI123')

    # Déterminez la date du dernier jour ouvrable
    last_day = last_business_day()
    remote_filename = f'operations/Op_de_change{last_day.strftime("%Y-%m-%d")}.xlsx'

    temp_filename = None  # Initialisation de temp_filename

    try:
        # Connexion au serveur FTP
        with ftplib.FTP(ftp_server) as ftp:
            ftp.login(username, password)

            # Vérifier si le fichier existe sur le serveur
            files = ftp.nlst('operations')  # Obtenez la liste des fichiers dans le répertoire 'operations'
            if remote_filename not in files:
                return HttpResponse("Aucun fichier disponible pour le dernier jour ouvrable.", status=404)

            # Télécharger le fichier s'il existe
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
                ftp.retrbinary(f'RETR {remote_filename}', temp_file.write)
                temp_filename = temp_file.name

        # Lire le fichier Excel téléchargé
        data = pd.read_excel(temp_filename)

        # Injecter les données dans la base de données en évitant les doublons
        for index, row in data.iterrows():
            nooper = row['NOOPER']
            datoper = row['DATOPER']
            if not OperationCorp.objects.filter(nooper=nooper, datoper=datoper).exists():
                OperationCorp.objects.create(
                    modev=row['MODEV'],
                    nooper=nooper,
                    datoper=datoper,
                    devisec=row['DEVISEC'],
                    devised=row['DEVISED'],
                    mntdevd=row['MNTDEVD'],
                    mntdevc=row['MNTDEVC'],
                    cours12=row['COURS12'],
                    nomd=row['NOMD'],
                    libelle=row['LIBELLE'],
                    client=row['CLIENT'],
                    comptec=row['COMPTEC'],
                    agence=row['AGENCE'],
                )

        return HttpResponse("Données chargées avec succès dans la base de données.")

    except ftplib.all_errors as e:
        return HttpResponse(f"Erreur FTP : {e}", status=500)
    except Exception as e:
        return HttpResponse(f"Erreur lors du chargement des données : {e}", status=500)
    finally:
        if temp_filename and os.path.exists(temp_filename):
            os.remove(temp_filename)


# Assurez-vous d'importer HttpResponse de django.http
from django.http import HttpResponse



# views.py
from django.http import JsonResponse
from app.tasks import download_and_inject

def trigger_task(request):
    try:
        download_and_inject.delay()
        return JsonResponse({'status': 'Task has been triggered'})
    except Exception as e:
        return JsonResponse({'status': 'Error', 'message': str(e)})






# def import_corp(request):
#     if request.method == 'POST':
#         excel_file = request.FILES.get("excel_file")
#         if not excel_file:
#             return HttpResponse("No file uploaded", status=400)

#         try:
#             df = pd.read_excel(excel_file)
#         except Exception as e:
#             return HttpResponse(f"Error reading the file: {e}", status=500)

#         operationcorp = []
#         for index, row in df.iterrows():
#             try:
#                 OperationCorp.append(OperationCorp(
#                     modev=row['MODEV'],
#                     nooper=row['NOOPER'],
#                     datoper=pd.to_datetime(row['DATOPER']),
#                     devisec=row['DEVISEC'],
#                     devised=row['DEVISED'],
#                     mntdevd=row['MNTDEVD'],
#                     mntdevc=row['MNTDEVC'],
#                     cours12=row['COURS12'],
#                     nomd=row['NOMD'],
#                     libelle=row['LIBELLE'],
#                     client=row['CLIENT'],
#                     comptec=row['COMPTEC'],
#                     agence=row['AGENCE'],
#                 ))
#             except KeyError as e:
#                 return HttpResponse(f"Missing data for {e}", status=400)
        
#         # Using bulk_create to optimize db inserts
#         OperationCorp.objects.bulk_create(operationcorp)

#         return redirect('/view')

#     return render(request, 'corpform.html')




def view_corp(request):
    transactions = OperationCorp.objects.all()
    return render(request, 'list.html', {'transactions': transactions})




def RisqueLimite(request):
    # Obtenez la date et l'heure actuelles
    now = datetime.now()
    
    # Calculez la date et l'heure il y a 48 heures
    start_date = now - timedelta(hours=48)
    
    # Calculez le total des achats en devise USD dans les 48 dernières heures pour chaque contrepartie
    operations = Operation.objects.filter(date_operation__gte=start_date, devise_achat='USD').values('conterpartie').annotate(total_achat=Sum('montant_achat'))
    
    # Récupérez les limites de contreparties pour chaque contrepartie
    limites = LimiteContrepartie.objects.all()
    
    # Créez une liste pour stocker les données de chaque contrepartie
    resultats = []
    for limite in limites:
        total_achat = operations.filter(conterpartie=limite.conterpartie).aggregate(total_achat=Sum('montant_achat')).get('total_achat', 0)
        if total_achat is None:
            total_achat = 0
        montant_restant = limite.limite - total_achat if limite.limite is not None else None
        
        # Créez un objet contenant les données de chaque contrepartie
        resultat = {
            'conterpartie': limite.conterpartie,
            'total_achat': total_achat,
            'limite': limite.limite,
            'montant_restant': montant_restant
        }
        resultats.append(resultat)
    
    # Envoyez les données calculées au template
    return render(request, 'risque.html', {'resultats': resultats})








def add_limite(request):
    if request.method == "POST":
        form = LimiteForm(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            # messages.success(request,"L'operation  a été ajouté avec succès")
        return redirect('RisqueLimite')
    else:
        form = LimiteForm()
    return render(request, 'risque.html', {'form': form})


