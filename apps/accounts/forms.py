from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'role') 
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-3 border'
            })

class UserUpdateForm(forms.ModelForm):
    """
    Formulaire pour modifier les infos de compte (Nom, Prénom, Tél).
    """
    class Meta:
        model = CustomUser
        fields = ['last_name', 'first_name', 'email', 'phone']
        labels = {
            'last_name': 'Nom de famille',
            'first_name': 'Prénom',
            'email': 'Adresse Email',
            'phone': 'Numéro de téléphone'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2.5 border bg-gray-50'
            })