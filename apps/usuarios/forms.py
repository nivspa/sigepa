from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Usuario


class UsuarioCreationForm(UserCreationForm):
    """
    Formulário personalizado para criação de usuários.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    telefone = forms.CharField(max_length=20, required=False)
    data_nascimento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_nascimento'].widget.attrs['max'] = timezone.localdate().isoformat()

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'telefone', 'data_nascimento', 'password1', 'password2')
    
    def clean_data_nascimento(self):
        """Valida que a data de nascimento não seja no futuro"""
        data = self.cleaned_data.get('data_nascimento')
        if data and data > timezone.localdate():
            raise ValidationError('A data de nascimento não pode ser no futuro.')
        return data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.telefone = self.cleaned_data['telefone']
        user.data_nascimento = self.cleaned_data['data_nascimento']
        if commit:
            user.save()
        return user
