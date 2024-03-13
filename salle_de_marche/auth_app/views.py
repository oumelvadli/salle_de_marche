from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from .form import CustomUerCreatinForm
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from app import views



def inscription(request):
    if request.method=='POST':
        form=CustomUerCreatinForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('connexion')
    else:
        form=CustomUerCreatinForm()
    return render(request,'inscription.html',{'form':form})

def connexion(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect("Accueil")
        else:
            messages.error(request,'nom d\'utilisateur ou mot de passe incorrect. ')
    return render(request, 'connexion.html')


def deconnexion(request):
    logout(request)
    return redirect('connexion')


# Create your views here.
