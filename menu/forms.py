from django import forms

from .models import CategoriaMenu, ItemMenu


class CategoriaMenuForm(forms.ModelForm):
    class Meta:
        model = CategoriaMenu
        fields = ['nombre', 'tipo', 'descripcion', 'orden', 'activa']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = 'form-control'
            if isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            elif isinstance(field.widget, forms.CheckboxInput):
                css_class = 'form-check-input'
            field.widget.attrs['class'] = css_class


class ItemMenuForm(forms.ModelForm):
    class Meta:
        model = ItemMenu
        fields = [
            'categoria', 'nombre', 'descripcion', 'precio',
            'imagen', 'external_image_url', 'tiene_oferta', 'precio_oferta',
            'disponible', 'destacado', 'orden',
            'anno', 'bodega', 'origen', 'cepa', 'graduacion'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'external_image_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = 'form-control'
            if isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            elif isinstance(field.widget, forms.CheckboxInput):
                css_class = 'form-check-input'
            field.widget.attrs['class'] = css_class
        self.fields['imagen'].help_text = 'Las imagenes de carta se guardan en media/menu/items/.'

    def clean(self):
        cleaned_data = super().clean()
        tiene_oferta = cleaned_data.get('tiene_oferta')
        precio = cleaned_data.get('precio')
        precio_oferta = cleaned_data.get('precio_oferta')

        if tiene_oferta and not precio_oferta:
            self.add_error('precio_oferta', 'Debes indicar el precio de oferta.')
        if tiene_oferta and precio and precio_oferta and precio_oferta >= precio:
            self.add_error('precio_oferta', 'El precio de oferta debe ser menor al precio normal.')
        if not tiene_oferta:
            cleaned_data['precio_oferta'] = None
        return cleaned_data
