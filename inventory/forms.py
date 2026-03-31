from django import forms
from .models import StockMovement


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['movement_type', 'quantity', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }