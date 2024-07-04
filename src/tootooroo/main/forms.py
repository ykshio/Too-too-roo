from django import forms
from main.models import Toot

class TootForm(forms.ModelForm):
    class Meta:
        model = Toot
        fields = ['content']
