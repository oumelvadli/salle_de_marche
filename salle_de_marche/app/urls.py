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
]