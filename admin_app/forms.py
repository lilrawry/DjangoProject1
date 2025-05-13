from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Administrateur

class AdminLoginForm(forms.Form):
    username = forms.CharField(
        label='Nom d\'utilisateur',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre nom d\'utilisateur'})
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre mot de passe'})
    )

class AdminRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre email'})
    )
    telephone = forms.CharField(
        label='Téléphone',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre numéro de téléphone'})
    )

    class Meta:
        model = Administrateur
        fields = ('username', 'email', 'telephone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Choisissez un nom d\'utilisateur'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Créez un mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmez le mot de passe'}) 