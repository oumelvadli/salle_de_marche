from django.db import models
from django.contrib.auth.models import AbstractUser





class Utilisateur(models.Model):
    nom=models.CharField(max_length=50)
    password=models.CharField(max_length=10)





# Create your models here.
