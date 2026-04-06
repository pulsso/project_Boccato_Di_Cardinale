from django.db import models


def _local_menu_fallback(tipo):
    file_by_tipo = {
        'desayuno': 'desayuno.jpg',
        'brunch': 'brunch.jpg',
        'almuerzo': 'almuerzo.jpg',
        'postres': 'postres.jpg',
        'infantil': 'infantil.jpg',
        'te_cafe': 'te_cafe.jpg',
        'bebidas': 'bebidas.jpg',
        'llevar': 'llevar.jpg',
        'cena': 'cena.jpg',
        'terraza': 'terraza.jpg',
        'vinos': 'vinos.jpg',
        'licores': 'licores.jpg',
        'cocteles': 'cocteles.jpg',
        'catering': 'catering.jpg',
    }
    return f"/static/menu/photos/{file_by_tipo.get(tipo, 'almuerzo.jpg')}"


class CategoriaMenu(models.Model):
    TIPO_CHOICES = [
        ('desayuno', 'Menu Desayuno'),
        ('brunch', 'Brunch y Once'),
        ('almuerzo', 'Menu Almuerzo'),
        ('postres', 'Postres'),
        ('infantil', 'Menu Infantil Dia'),
        ('te_cafe', 'Te - Cafe e Infusiones'),
        ('bebidas', 'Bebidas y Cervezas'),
        ('llevar', 'Para Llevar y Boutique'),
        ('cena', 'Menu Cena'),
        ('terraza', 'Menu Terraza'),
        ('vinos', 'Carta de Vinos'),
        ('licores', 'Licores y Whiskies'),
        ('cocteles', 'Cocteles'),
        ('catering', 'Catering y Eventos'),
    ]
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['tipo', 'orden']
        verbose_name = 'Categoria de Menu'
        verbose_name_plural = 'Categorias de Menu'

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.nombre}'


class ItemMenu(models.Model):
    categoria = models.ForeignKey(CategoriaMenu, on_delete=models.CASCADE, related_name='items')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    imagen = models.ImageField(upload_to='menu/items/', blank=True, null=True)
    external_image_url = models.URLField(blank=True, verbose_name='Imagen externa (URL)')
    tiene_oferta = models.BooleanField(default=False)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    disponible = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    anno = models.CharField(max_length=10, blank=True, verbose_name='Ano')
    bodega = models.CharField(max_length=100, blank=True, verbose_name='Bodega/Marca')
    origen = models.CharField(max_length=100, blank=True, verbose_name='Origen/Valle')
    cepa = models.CharField(max_length=100, blank=True, verbose_name='Cepa/Tipo')
    graduacion = models.CharField(max_length=20, blank=True, verbose_name='Graduacion')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Item de Menu'
        verbose_name_plural = 'Items de Menu'

    def __str__(self):
        return f'{self.nombre} - ${self.precio}'

    @property
    def display_image_url(self):
        if self.imagen:
            return self.imagen.url
        if self.external_image_url:
            return self.external_image_url
        fallback_by_tipo = {
            'desayuno': _local_menu_fallback('desayuno'),
            'brunch': _local_menu_fallback('brunch'),
            'almuerzo': _local_menu_fallback('almuerzo'),
            'postres': _local_menu_fallback('postres'),
            'infantil': _local_menu_fallback('infantil'),
            'te_cafe': _local_menu_fallback('te_cafe'),
            'bebidas': _local_menu_fallback('bebidas'),
            'llevar': _local_menu_fallback('llevar'),
            'cena': _local_menu_fallback('cena'),
            'terraza': _local_menu_fallback('terraza'),
            'vinos': _local_menu_fallback('vinos'),
            'licores': _local_menu_fallback('licores'),
            'cocteles': _local_menu_fallback('cocteles'),
            'catering': _local_menu_fallback('catering'),
        }
        return fallback_by_tipo.get(self.categoria.tipo, '')

    @property
    def descuento_porcentaje(self):
        if not self.tiene_oferta or not self.precio_oferta or not self.precio:
            return 0
        descuento = (1 - (self.precio_oferta / self.precio)) * 100
        return max(0, round(descuento))
