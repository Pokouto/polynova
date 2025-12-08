from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """
    Formulaire d'inscription public.
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'role') 
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # --- SÉCURITÉ : SUPPRESSION DU RÔLE ADMIN ---
        # On récupère les choix définis dans le modèle, mais on exclut 'admin'
        # Seuls 'parent' et 'tutor' seront visibles dans la liste déroulante.
        self.fields['role'].choices = [
            (code, label) for code, label in CustomUser.ROLE_CHOICES if code != 'admin'
        ]
        # ---------------------------------------------
        
        # Style commun pour tous les champs
        common_style = 'block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg bg-gray-50 text-gray-900 placeholder-gray-400 focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent sm:text-sm transition duration-200 ease-in-out shadow-sm'
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': common_style,
                'placeholder': field.label
            })


class UserUpdateForm(forms.ModelForm):
    """
    Formulaire de modification de profil (Espace Membre).
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
        # Style Tailwind pour les champs de modification
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2.5 border bg-gray-50 transition duration-150 ease-in-out'
            })