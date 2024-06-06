from django.urls import path
from . import views


urlpatterns = [
    path('Accueil/',views.Accueil,name="Accueil"),
    path('MarketData/',views.MarketData,name="MarketData"),
    path('traitmentt/',views.Traitment,name="Traitment"),

    path('add_cours/',views.add_cours,name="add_cours"),
    path('add_bande/',views.add_bande,name="add_bande"),
    path('update_cours/<int:id>', views.update_cours, name="update_cours"),
    path('update_bande/<int:id>', views.update_bande, name="update_bande"),
    path('importer/',views.importer_donnees,name="importer_donnes"),
    path('visualisation/',views.visualisation,name="visualisation"),
    path('operation/<int:id>/update/',views.update_operation,name="update_operation"),
    path('operation/<int:id>/delete/',views.delete_operation,name="delete_operation"),
    path('addoperation/',views.add_operation,name="add_operation"),

    path('position/',views.calcul_position,name="calcul"),
    path('meilleures_contreparties/',views.meilleures_contreparties,name="meilleures_contreparties"),
    path('filter_operations/',views.filter_operations,name="filter_operations"),
    path('EoD/', views.EoD, name='EoD'),
    path('export_to_excel_operations/', views.export_to_excel_operations, name='export_to_excel_operations'),
    path('export_to_excel_reporting/', views.export_to_excel_reporting, name='export_to_excel_reporting'),



    path('users/',views.gestion_utilisateurs,name="users"),
    path('inscription',views.inscription,name="inscription"),


    path('toggle_user_active/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change_password/<int:user_id>/', views.change_password, name='change_password'),



    path('operation/<int:operation_id>/download/', views.download_ticket, name='download_ticket'),

    #     path('', views.vue_principale,  name='vue_principale'),
    # path('update_date_ouverture/', views.update_date_ouverture, name='update_date_ouverture'),
    # path('update_date_fermeture/', views.update_date_fermeture, name='update_date_fermeture'),


    # path('h/', views.limit, name='check_threshold'),
    # path('t/', views.Alert, name='alert'),
    # path('test/<str:task_id>/', views.test_recup, name='recup'),
    path('update_session/', views.update_session, name='update_session'),
    path('task/', views.trigger_task, name='task'),
    path('view/', views.view_corp, name='view_corp'),
    path('ftp/', views.list_ftp_files, name='listftp'),
    path('operationcorp/', views.visualisationCorp, name='OperationCorp'),
    path('filter_operationscorp/', views.filter_operationscorp, name='filter_operationscorp'),
    path('RisqueLimite/', views.RisqueLimite, name='RisqueLimite'),
    path('add_limite/', views.add_limite, name='add_limite'),












   

]