# # Importations nécessaires
# from django.http import HttpResponseRedirect
# from django.urls import reverse
# from datetime import date
# from .models import Journee

# # Définition de la classe Middleware
# class VerificationJourneeMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if not request.path.startswith(reverse('ouvrir_journee')) and not request.path.startswith(reverse('fermer_journee')):
#             journee_en_cours, created = Journee.objects.get_or_create(date=date.today())
#             if not journee_en_cours.ouvert:
#                 return HttpResponseRedirect(reverse('journee_non_ouverte'))
#             elif journee_en_cours.ferme:
#                 return HttpResponseRedirect(reverse('journee_fermee'))
#         response = self.get_response(request)
#         return response
