from django import forms
from .models import Mesa


class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['numero', 'zona', 'capacidad', 'activa', 'pos_x', 'pos_y']
        help_texts = {
            'pos_x': 'Posición horizontal en el mapa (0-100)',
            'pos_y': 'Posición vertical en el mapa (0-100)',
        }