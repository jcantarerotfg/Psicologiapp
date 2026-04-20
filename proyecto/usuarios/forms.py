from django import forms
from django.contrib.auth.models import User

class CambiarPasswordForm(forms.Form):
    nuevo_pass = forms.CharField(
        widget=forms.PasswordInput(),
        label="Nueva contraseña",
        required = True,
        error_messages={'required': 'Debe ingresar una nueva contraseña'}
    )