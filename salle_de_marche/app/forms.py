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