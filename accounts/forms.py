from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from config.commerce import SECTOR_CHOICES, ZONE_CHOICES


class CustomerRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=False, label='Nombre')
    last_name = forms.CharField(max_length=150, required=False, label='Apellido')
    email = forms.EmailField(required=True, label='Email')
    zone = forms.ChoiceField(choices=ZONE_CHOICES, label='Zona')
    sector = forms.ChoiceField(choices=SECTOR_CHOICES, label='Sector')
    default_address = forms.CharField(
        required=False,
        label='Direccion inicial',
        widget=forms.Textarea(attrs={'rows': 3}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'zone', 'sector', 'default_address', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = 'form-control'
            if isinstance(field.widget, forms.Select):
                css = 'form-select'
            field.widget.attrs.setdefault('class', css)
