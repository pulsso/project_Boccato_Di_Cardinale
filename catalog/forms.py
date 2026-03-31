from django import forms

from .models import Campana, GaleriaFoto, Oferta, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'slug',
            'description',
            'price',
            'stock',
            'image',
            'external_image_url',
            'available',
            'featured',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = 'Las imagenes de tienda se guardan en media/products/store/.'


class OfertaForm(forms.ModelForm):
    class Meta:
        model = Oferta
        fields = ['producto', 'descuento_porcentaje', 'fecha_inicio', 'fecha_fin', 'activa']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }


class CampanaForm(forms.ModelForm):
    class Meta:
        model = Campana
        fields = ['titulo', 'subtitulo', 'imagen', 'tipo', 'url_destino', 'activa', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }


class GaleriaFotoForm(forms.ModelForm):
    class Meta:
        model = GaleriaFoto
        fields = ['titulo', 'descripcion', 'imagen', 'external_image_url', 'seccion', 'orden', 'activa']
