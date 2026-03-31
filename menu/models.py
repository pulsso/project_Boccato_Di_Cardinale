from django.db import models


class CategoriaMenu(models.Model):
    TIPO_CHOICES = [
        ('desayuno', 'Menu Desayuno'),
        ('brunch', 'Brunch y Once'),
        ('almuerzo', 'Menu Almuerzo'),
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
        return self.external_image_url or ''
