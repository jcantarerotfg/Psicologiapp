from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class CambiarPasswordForm(forms.Form):
    nuevo_pass = forms.CharField(
        widget=forms.PasswordInput(),
        label="Nueva contraseña",
        required = True,
        error_messages={'required': 'Debe ingresar una nueva contraseña'}
    )

    def clean_nuevo_pass(self):
        password = self.cleaned_data.get('nuevo_pass')
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return password