from django.shortcuts import render

# Create your views here.
def Accueil(request):
    return render(request,"Accueil.html",{'navbar':'Accueil'})

def MarketData(request):
    return render(request,"MarketData.html",{'navbar':'MarketData'})