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

    class Meta:
        model = CourseRequest
        fields = ['level', 'subjects', 'city', 'quartier', 'frequency', 'budget_range', 'is_online', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ex: Mon fils a des lacunes en géométrie...'}),
            'quartier': forms.TextInput(attrs={'placeholder': 'Ex: Riviera 2, Marcory Zone 4...'}),
            'frequency': forms.TextInput(attrs={'placeholder': 'Ex: Mercredi après-midi et Samedi matin'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style Tailwind global
        for name, field in self.fields.items():
            if name != 'subjects' and name != 'is_online':
                field.widget.attrs.update({'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border'})


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
        # Style Tailwind spécifique pour le commentaire
        self.fields['comment'].widget.attrs.update({'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border'})