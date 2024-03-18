from .models import *
from django import forms


class Cours_revaluationForm(forms.ModelForm):
    class Meta:
        model= Cours_revaluation
        fields = "__all__"

class Bande_fluctuationForm(forms.ModelForm):
    class Meta:
        model= Bande_fluctuation
        fields = "__all__"
        
class ExcelImportForm(forms.Form):
    fichier_excel = forms.FileField()

class DateFilterForm(forms.Form):
    date = forms.DateField(label='Filtrer par date', required=False)