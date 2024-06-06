from .models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm


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

class OperationForm(forms.ModelForm):
    class Meta:
        model = Operation
        fields = '__all__'

class LimiteForm(forms.ModelForm):
    class Meta:
        model = LimiteContrepartie
        fields = '__all__'



#========================= create user =====================

class CustomUerCreationForm(UserCreationForm):
    password1=forms.CharField(
        label="password",
        strip=False,
        widget=forms.PasswordInput( attrs={'autocomplete':'new-password'})
    )

    password2=forms.CharField(
        label="password confirmation",
        strip=False,
        widget=forms.PasswordInput( attrs={'autocomplete':'new-password'})
    )

    class Meta(UserCreationForm.Meta):
        fields=UserCreationForm.Meta.fields + ( "password1","password2")