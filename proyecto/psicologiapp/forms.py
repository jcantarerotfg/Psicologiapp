from django import forms
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from usuarios.models import Usuario, PerfilPaciente, EvolucionPaciente, Paciente_Doctor
from psicologiapp.models import Diario, HistorialSesiones, RelacionTareas, Mensaje, Archivos

class EditarPerfilForm (forms.ModelForm):

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
                'class': 'form-control'}),
        required=False
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return password
    class Meta:
        model = Usuario
        fields = ['first_name','last_name','email','telefono','foto_perfil']
        widgets = {
            'foto_perfil' : forms.FileInput(),
            'username' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce un usuario'
            }),
            'first_name' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce el nombre del usuario'
            }),
            'last_name' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce los apellidos del usuario'
            }),
            'email' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce un email'
            }),
            'telefono' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce un teléfono'
            }),
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
        widget=forms.PasswordInput(attrs={
                'class': 'form-control'}),
        required=True,
        error_messages={'required': 'Debe indicar una contraseña temporal para el usuario'}
    )
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return password
    class Meta:
        model = Usuario
        fields = ['username','first_name','last_name','email','telefono','foto_perfil','rol', 'chat']
        widgets = {
            'foto_perfil' : forms.FileInput(),
            'username' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce un usuario'
            }),
            'first_name' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce el nombre del usuario'
            }),
            'last_name' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce los apellidos del usuario'
            }),
            'email' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce un email'
            }),
            'telefono' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce un teléfono'
            }),
            'chat': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch',
            }),
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
                self.fields['rol'].required = False
                self.fields['rol'].disabled = True
                self.fields['doctor'].initial = self.usuario
                self.fields['doctor'].disabled = True

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

class EditarUsuarioForm (forms.ModelForm):

    doctor = DoctorChoiceField(
        queryset=Usuario.objects.filter(rol='doctor'),
        required=False,
        label='Psicologo responsable',
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
                'class': 'form-control'}),
        required=False
    )
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return password
    class Meta:
        model = Usuario
        fields = ['username','first_name','last_name','email','telefono','foto_perfil', 'chat', 'rol']
        widgets = {
            'foto_perfil' : forms.FileInput(),
            'username' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce un usuario'
            }),
            'first_name' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce el nombre del usuario'
            }),
            'last_name' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce los apellidos del usuario'
            }),
            'email' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce un email'
            }),
            'telefono' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce un teléfono'
            }),
            'chat': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        print("KWARGS:", kwargs)
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            try:
                relacion = Paciente_Doctor.objects.get(paciente=self.instance)
                self.fields['doctor'].initial = relacion.doctor
            except Paciente_Doctor.DoesNotExist:
                pass

        if self.usuario:
            if self.usuario.rol == 'doctor':
                self.fields['rol'].choices = [("paciente","Paciente")]
                self.fields['rol'].required = False
                self.fields['rol'].disabled = True
                self.fields['rol'].widget.attrs['disabled'] = True
                self.fields['doctor'].initial = self.usuario
                self.fields['doctor'].disabled = True
                self.fields['doctor'].widget.attrs['disabled'] = True

            else:
                self.fields['rol'].choices = [("paciente","Paciente"), ("doctor", "Doctor") ,("admin","Administrador")]
                self.fields['rol'].required = True
                self.fields['rol'].initial = "paciente"
    
    def save(self, commit =True):
        usuario = super().save(commit=False)
        passw = self.cleaned_data.get('password')

        if passw:
            usuario.set_password(passw)
            usuario.pass_temporal = True
        if commit:
            usuario.save()
        return usuario

class DiarioForm (forms.ModelForm):
    class Meta:
        model = Diario
        fields = ['titulo', 'contenido', 'estado_animo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '¿Qué título le pondrías a tu día?'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': '¡Cúentame un poco como ha ido tu día!'
            }),
            'estado_animo': forms.NumberInput(attrs={
                'type': 'range',
                'class': 'form-range',
                'min': 1,
                'max': 5,
                'step': 1,
            }),
        }


class LeerDiarioForm (forms.ModelForm):
    class Meta:
        model = Diario
        fields = ['titulo', 'contenido', 'estado_animo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '¿Qué título le pondrías a tu día?',
                'disabled': 'disabled'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': '¡Cúentame un poco como ha ido tu día!',
                'disabled': 'disabled'
            }),
            'estado_animo': forms.NumberInput(attrs={
                'type': 'range',
                'class': 'form-range',
                'min': 1,
                'max': 5,
                'step': 1,
                'disabled': 'disabled'
            }),
        }

class PerfilPacienteForm(forms.ModelForm):
    class Meta:
        model = PerfilPaciente
        fields = ['evolucion', 'puntos_fuertes', 'puntos_debiles']
        widgets = {
            'evolucion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Evolución del paciente',
            }),
            'puntos_fuertes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Puntos fuertes del paciente',
            }),
            'puntos_debiles': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Puntos debiles del paciente',
            }),
        }

class EvolucionPacienteForm(forms.ModelForm):
    fecha_comentario = forms.DateField(
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }, format='%Y-%m-%d')
    )
    class Meta:
        model = EvolucionPaciente
        fields = ['fecha_comentario', 'comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Comentario de evolución',
                'required': False,
            }),
        }

class NuevaSesionForm(forms.ModelForm):
    fecha_sesion = forms.DateField(
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }, format='%Y-%m-%d')
    )
    class Meta:
        model = HistorialSesiones
        fields = ['fecha_sesion', 'resumen_sesion', 'observaciones']
        widgets = {
            'resumen_sesion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Resumen de la sesión',
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Observaciones',
            }),
        }

class RelacionTareasForm(forms.ModelForm):
    fecha_tareas = forms.DateField(
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }, format='%Y-%m-%d')
    )
    class Meta:
        model = RelacionTareas
        fields = ['fecha_tareas', 'observacion_doctor']
        widgets = {
            'observacion_doctor': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Observaciones',
                'required': True
            }),
        }

class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['contenido']
        widgets = {
            'contenido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mensaje',
                'autocomplete': 'off',
            }),
        }
class ArchivosForm(forms.ModelForm):
    class Meta:
        model = Archivos
        fields = ['archivo']
        widgets = {
            'archivo' : forms.FileInput(attrs={
                    'class': 'form-control',
                }),
        }