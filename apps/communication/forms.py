from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Écrivez votre message...',
                'class': 'block w-full rounded-md border-gray-300 shadow-sm p-3 border'
            }),
        }