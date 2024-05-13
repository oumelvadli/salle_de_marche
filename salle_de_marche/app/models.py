from django.db import models

# Create your models here.

class Cours_revaluation(models.Model):
    date = models.DateField(null=False)
    devise = models.CharField(null=False,max_length=15)
    cours = models.FloatField(null=False)
    
    
class Bande_fluctuation(models.Model):
    date = models.DateField(null=False)
    devise = models.CharField(null=False,max_length=15)
    Bid = models.FloatField(null=False)
    Ask = models.FloatField(null=False)



class Operation(models.Model):
    id = models.AutoField(primary_key=True, unique=True, editable=False) 
    date_operation = models.DateField()
    date_validation = models.DateField()
    conterpartie = models.CharField(max_length=50)
    devise_achat = models.CharField(max_length=5)
    devise_vente = models.CharField(max_length=5)
    cours = models.DecimalField(max_digits=5, decimal_places=2)
    montant_achat = models.DecimalField(max_digits=20, decimal_places=2)
    montant_vendu = models.DecimalField(max_digits=20, decimal_places=2)
    type = models.CharField(max_length=20)
    direction = models.CharField(max_length=10, blank=False,default='None')
    

class Journee(models.Model):
    date_overture = models.DateField(unique=True)
    date_fermeture = models.DateTimeField(null=True, blank=True)
    est_ouvert = models.BooleanField(default=False)

class Test(models.Model):
    nom=models.CharField(max_length=50)
    prenom=models.CharField(max_length=50)
    
    
    

class SessionStatus(models.Model):
    is_open = models.BooleanField(default=False)
    start_jour = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_jour = models.DateField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)


