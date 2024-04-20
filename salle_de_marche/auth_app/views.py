from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from .form import CustomUerCreationForm
from django.contrib import messages
from app import views
from django.contrib.auth import authenticate, login, get_user_model,logout
from django.core.cache import cache



def inscription(request):
    if request.method=='POST':
        form=CustomUerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('connexion')
    else:
        form=CustomUerCreationForm()
    return render(request,'inscription.html',{'form':form})

def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        failed_attempts = cache.get(username, 0)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                if user.is_authenticated:
                    login(request, user)
                    cache.set(username, 0, timeout=None)
                    return redirect('Accueil')
                else:
                    messages.error(request, 'Authentication failed.')
            else:
                messages.error(request, 'Votre compte est désactivé. Veuillez contacter l\'administrateur.')
        else:
            failed_attempts += 1
            cache.set(username, failed_attempts, timeout=3600)  

            if failed_attempts >= 3:
                User = get_user_model()
                try:
                    user_to_deactivate = User.objects.get(username=username)
                    user_to_deactivate.is_active = False
                    user_to_deactivate.save()
                    messages.error(request, 'Votre compte a été désactivé après trois tentatives infructueuses.')
                except User.DoesNotExist:
                    messages.error(request, 'Aucun compte trouvé avec ce nom d\'utilisateur.')

            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')

    return render(request, 'connexion.html')


def deconnexion(request):
    logout(request)
    return redirect('connexion')


# Create your views here.
