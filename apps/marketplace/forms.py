from django import forms
from .models import CourseRequest, Review
from apps.education.models import Subject, Level
from apps.core.models import City

class RequestForm(forms.ModelForm):
    """
    Formulaire pour créer/modifier une demande de cours (Parent).
    """
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm p-2', 'style': 'height: 120px'}),
        label="Matières (Maintenir CTRL pour plusieurs)"
    )
    
    # Case obligatoire pour conformité RGPD/Contact
    terms_accepted = forms.BooleanField(
        required=True, 
        label="J’accepte d’être contacté(e) par des enseignants vérifiés via la plateforme."
    )

    class Meta:
        model = CourseRequest
        fields = ['level', 'subjects', 'city', 'quartier', 'start_time', 'frequency', 'intention', 'budget_range', 'is_online', 'description']
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ex: Mon fils a des lacunes en géométrie...'}),
            'quartier': forms.TextInput(attrs={'placeholder': 'Ex: Riviera 2, Marcory Zone 4...'}),
            'frequency': forms.TextInput(attrs={'placeholder': 'Ex: Mercredi après-midi et Samedi matin'}),
            # Boutons Radio pour l'intention
            'intention': forms.RadioSelect(attrs={'class': 'form-radio text-orange-500 h-4 w-4'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style Tailwind global pour les champs standards
        common_style = 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border'
        
        for name, field in self.fields.items():
            # On n'applique pas ce style aux widgets spéciaux (Radio, Checkbox, SelectMultiple)
            if name not in ['subjects', 'intention', 'is_online', 'terms_accepted']:
                field.widget.attrs.update({'class': common_style})


class ReviewForm(forms.ModelForm):
    """
    Formulaire pour laisser un avis sur un prof.
    """
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Partagez votre expérience avec ce professeur...'}),
            'rating': forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs.update({'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border'})