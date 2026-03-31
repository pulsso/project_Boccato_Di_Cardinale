from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categorias'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/store/', blank=True, null=True)
    external_image_url = models.URLField(blank=True, verbose_name='Imagen externa (URL)')
    available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False, verbose_name='Destacado')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def display_image_url(self):
        if self.image:
            return self.image.url
        return self.external_image_url or ''

    def precio_con_oferta(self):
        oferta = self.ofertas.filter(activa=True).first()
        if oferta:
            descuento = self.price * oferta.descuento_porcentaje / 100
            return round(self.price - descuento, 2)
        return self.price


class GaleriaFoto(models.Model):
    SECCION_CHOICES = [
        ('terraza', 'Terraza Principal'),
        ('arte', 'Galeria de Arte'),
        ('vip', 'Salon VIP'),
        ('reuniones', 'Sala de Reuniones'),
        ('bar', 'La Barra'),
        ('puros', 'Terraza Puros'),
        ('musica', 'Musica en Vivo'),
    ]
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='galeria/', blank=True, null=True)
    external_image_url = models.URLField(blank=True, verbose_name='Imagen externa (URL)')
    seccion = models.CharField(max_length=20, choices=SECCION_CHOICES, default='terraza')
    orden = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)
    creada_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['seccion', 'orden']
        verbose_name = 'Foto de Galeria'
        verbose_name_plural = 'Galeria de Fotos'

    def __str__(self):
        return f'{self.get_seccion_display()} - {self.titulo}'

    @property
    def display_image_url(self):
        if self.imagen:
            return self.imagen.url
        return self.external_image_url or ''


class Oferta(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ofertas')
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Descuento %')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activa = models.BooleanField(default=True)
    creada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    creada_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creada_at']
        verbose_name = 'Oferta'
        verbose_name_plural = 'Ofertas'

    def __str__(self):
        return f'{self.producto.name} - {self.descuento_porcentaje}% off'


class Campana(models.Model):
    TIPO_CHOICES = [
        ('banner', 'Banner Principal'),
        ('popup', 'Popup'),
        ('destacado', 'Seccion Destacada'),
    ]
    titulo = models.CharField(max_length=200)
    subtitulo = models.CharField(max_length=300, blank=True)
    imagen = models.ImageField(upload_to='campanas/', blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='banner')
    url_destino = models.CharField(max_length=300, blank=True, help_text='URL al hacer click')
    activa = models.BooleanField(default=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    creada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    creada_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creada_at']
        verbose_name = 'Campana'
        verbose_name_plural = 'Campanas'

    def __str__(self):
        return f'{self.titulo} ({self.get_tipo_display()})'


class HistorialCambio(models.Model):
    ACCION_CHOICES = [
        ('crear', 'Creacion'),
        ('editar', 'Edicion'),
        ('eliminar', 'Eliminacion'),
        ('precio', 'Cambio de precio'),
        ('stock', 'Cambio de stock'),
        ('oferta', 'Oferta creada'),
        ('campana', 'Campana creada'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    modelo = models.CharField(max_length=50)
    objeto_id = models.PositiveIntegerField(null=True, blank=True)
    objeto_nombre = models.CharField(max_length=200, blank=True)
    detalle = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Historial de Cambio'
        verbose_name_plural = 'Historial de Cambios'

    def __str__(self):
        return f'{self.usuario} - {self.get_accion_display()} - {self.objeto_nombre}'
