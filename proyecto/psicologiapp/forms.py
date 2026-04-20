from django import forms
from usuarios.models import Usuario

class EditarPerfilForm (forms.ModelForm):

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(),
        required=False
    )
    class Meta:
        model = Usuario
        fields = ['username','first_name','last_name','email','telefono','foto_perfil']
        widgets = {
            'foto_perfil' : forms.FileInput(),
        }
    
    def save(self, commit =True):
        usuario = super().save(commit=False)
        passw = self.cleaned_data.get('password')

        if passw:
            usuario.set_password(passw)
        if commit:
            usuario.save()
        return usuario

class DoctorChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
class CrearUsuarioForm (forms.ModelForm):

    doctor = DoctorChoiceField(
        queryset=Usuario.objects.filter(rol='doctor'),
        required=False,
        label='Psicologo responsable',
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(),
        required=True,
        error_messages={'required': 'Debe indicar una contraseña temporal para el usuario'}
    )
    class Meta:
        model = Usuario
        fields = ['username','first_name','last_name','email','telefono','foto_perfil','rol']
        widgets = {
            'foto_perfil' : forms.FileInput(),
        }
        error_messages = {
            'username': {
                'required': 'Debe indicar un nombre de usuario'
            },
        }
    def __init__(self, *args, **kwargs):
        print("KWARGS:", kwargs)
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        if self.usuario:
            if self.usuario.rol == 'doctor':
                self.fields['rol'].choices = [("paciente","Paciente")]
                self.fields['rol'].required = True
                self.fields['rol'].disabled = True
            else:
                self.fields['rol'].choices = [("paciente","Paciente"), ("doctor", "Doctor") ,("admin","Administrador")]
                self.fields['rol'].required = True
                self.fields['rol'].initial = "paciente"
            

    def save(self, commit =True):
        usuario = super().save(commit=False)
        usuario.pass_temporal = True
        passw = self.cleaned_data.get('password')

        if passw:
            usuario.set_password(passw)
        if commit:
            usuario.save()
        return usuario