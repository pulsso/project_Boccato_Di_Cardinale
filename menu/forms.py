from django import forms

from .models import CategoriaMenu, ItemMenu


class CategoriaMenuForm(forms.ModelForm):
    class Meta:
        model = CategoriaMenu
        fields = ['nombre', 'tipo', 'descripcion', 'orden', 'activa']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


class ItemMenuForm(forms.ModelForm):
    class Meta:
        model = ItemMenu
        fields = [
            'categoria', 'nombre', 'descripcion', 'precio',
            'imagen', 'external_image_url', 'disponible', 'destacado', 'orden',
            'anno', 'bodega', 'origen', 'cepa', 'graduacion'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'external_image_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['imagen'].help_text = 'Las imagenes de carta se guardan en media/menu/items/.'
