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

