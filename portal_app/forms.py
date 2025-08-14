from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()
USERNAME_FIELD = getattr(User, 'USERNAME_FIELD', 'username')  # ej: 'username' o 'email'

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repetir contraseña", widget=forms.PasswordInput)

    class Meta:
        model = User
        # Campos mínimos: el identificador y opcionalmente email si no es el USERNAME_FIELD
        if USERNAME_FIELD == 'email':
            fields = ['email']
        else:
            # Mantener también email si el modelo lo tiene
            base = [USERNAME_FIELD]
            if any(f.name == 'email' for f in User._meta.get_fields()):
                base.append('email')
            fields = base

        # Etiquetas más amigables
        labels = {USERNAME_FIELD: 'Usuario' if USERNAME_FIELD=='username' else USERNAME_FIELD.capitalize()}

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data['password1']
        user.set_password(password)
        if commit:
            user.save()
        return user
