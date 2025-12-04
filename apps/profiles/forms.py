from django import forms
from .models import TutorProfile, ParentProfile
from apps.education.models import Subject, Level

class TutorUpdateForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Quelles matières enseignez-vous ?",
        required=False
    )
    levels = forms.ModelMultipleChoiceField(
        queryset=Level.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Pour quels niveaux ?",
        required=False
    )

    class Meta:
        model = TutorProfile
        fields = [
            'bio', 'photo', 
            'city', 'quartier',
            'subjects', 'levels', 
            'is_home_class', 'is_online_class', 
            'cni_document', 'casier_judiciaire', 'diplomes_file'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'quartier': forms.TextInput(attrs={'placeholder': 'Ex: Riviera 2, Cocody...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['subjects', 'levels', 'is_home_class', 'is_online_class']:
                field.widget.attrs.update({
                    'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 p-2.5'
                })

class ParentUpdateForm(forms.ModelForm):
    """
    Formulaire pour modifier le profil Parent (Adresse).
    """
    class Meta:
        model = ParentProfile
        fields = ['address']
        labels = {
            'address': 'Adresse complète / Quartier'
        }
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': 'Ex: Cocody Riviera 2, Abidjan'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2.5 border bg-gray-50'
            })