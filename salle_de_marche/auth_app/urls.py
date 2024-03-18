from django.urls import path
from . import views


urlpatterns = [
    path('inscription',views.inscription,name="inscription"),
    path('',views.connexion,name="connexion"),
    path('deconnexion',views.deconnexion,name="deconnexion"),

]