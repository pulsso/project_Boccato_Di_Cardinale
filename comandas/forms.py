from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Mesa, PerfilGarzon


class MesaForm(forms.ModelForm):
    garzon_asignado = forms.ModelChoiceField(
        queryset=User.objects.filter(
            is_active=True
        ).filter(
            Q(is_superuser=True) | Q(is_staff=True) | Q(perfil_garzon__activo=True)
        ).distinct().order_by('username'),
        required=False,
        label='Responsable',
        empty_label='Sin asignar',
    )

    class Meta:
        model = Mesa
        fields = ['numero', 'zona', 'capacidad', 'activa', 'garzon_asignado', 'pos_x', 'pos_y']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'zona': forms.Select(attrs={'class': 'form-select'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'garzon_asignado': forms.Select(attrs={'class': 'form-select'}),
            'pos_x': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'pos_y': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class OperatorSwitchForm(forms.Form):
    codigo_operador = forms.IntegerField(
        min_value=1,
        label='Codigo',
        widget=forms.NumberInput(attrs={'placeholder': 'Codigo', 'inputmode': 'numeric'}),
    )
    pin = forms.CharField(
        label='PIN',
        strip=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'PIN', 'autocomplete': 'off'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        codigo = cleaned_data.get('codigo_operador')
        pin = cleaned_data.get('pin')
        if not codigo or not pin:
            return cleaned_data

        try:
            perfil = PerfilGarzon.objects.select_related('usuario').get(codigo_operador=codigo, activo=True)
        except PerfilGarzon.DoesNotExist:
            raise forms.ValidationError('No existe un operador activo con ese codigo.')

        if not perfil.check_pin(pin):
            raise forms.ValidationError('PIN incorrecto para el operador seleccionado.')

        cleaned_data['perfil'] = perfil
        return cleaned_data
