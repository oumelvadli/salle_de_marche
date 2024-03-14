from django.db import models

# Create your models here.

class Cours_revaluation(models.Model):
    date = models.DateField(null=False)
    devise = models.CharField(null=False,max_length=15)
    cours = models.FloatField(null=False)
    
    
class Bande_fluctuation(models.Model):
    date = models.DateField(null=False)
    devise = models.CharField(null=False,max_length=15)
    min = models.FloatField(null=False)
    max = models.FloatField(null=False)



class Operation(models.Model):
    date_operation = models.DateField()
    date_validation = models.DateField()
    conterpartie = models.CharField(max_length=50)
    devise_achat = models.CharField(max_length=5)
    devise_vente = models.CharField(max_length=5)
    cours = models.DecimalField(max_digits=5, decimal_places=2)
    montant_achat = models.DecimalField(max_digits=20, decimal_places=2)
    type = models.CharField(max_length=20)



