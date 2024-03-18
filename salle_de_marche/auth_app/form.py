from django import forms
from django.contrib.auth.forms import UserCreationForm

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
