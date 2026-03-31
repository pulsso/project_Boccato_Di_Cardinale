from django import forms
from .models import AperturaCaja, CierreCaja, Pago


class AperturaCajaForm(forms.ModelForm):
    class Meta:
        model = AperturaCaja
        fields = ['monto_inicial', 'notas']
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Observaciones opcionales...'}),
        }
        labels = {'monto_inicial': 'Monto inicial en caja ($)'}


class CierreCajaForm(forms.ModelForm):
    class Meta:
        model = CierreCaja
        fields = [
            'monto_efectivo', 'monto_tarjeta_credito',
            'monto_tarjeta_debito', 'monto_transferencia',
            'monto_propinas', 'notas'
        ]
        widgets = {'notas': forms.Textarea(attrs={'rows': 3})}
        labels = {
            'monto_efectivo':        'Total Efectivo ($)',
            'monto_tarjeta_credito': 'Total Tarjeta Credito ($)',
            'monto_tarjeta_debito':  'Total Tarjeta Debito ($)',
            'monto_transferencia':   'Total Transferencias ($)',
            'monto_propinas':        'Total Propinas ($)',
        }


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['metodo', 'propina', 'ultimos_4', 'referencia', 'notas']
        widgets = {
            'notas':     forms.Textarea(attrs={'rows': 2, 'placeholder': 'Observaciones...'}),
            'ultimos_4': forms.TextInput(attrs={'maxlength': 4, 'placeholder': '1234'}),
            'referencia': forms.TextInput(attrs={'placeholder': 'N° operacion o referencia'}),
        }
        labels = {
            'metodo':     'Metodo de pago',
            'propina':    'Propina ($)',
            'ultimos_4':  'Ultimos 4 digitos tarjeta',
            'referencia': 'Referencia/N° operacion',
            'notas':      'Notas',
        }


class AnulacionForm(forms.Form):
    motivo = forms.CharField(
        label='Motivo de la anulacion',
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Describa el motivo de la anulacion o reversa...'
        }),
        min_length=10,
        error_messages={'min_length': 'El motivo debe tener al menos 10 caracteres.'}
    )