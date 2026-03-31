# Generated manually for gallery external images.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_product_external_image_url_sample_products'),
    ]

    operations = [
        migrations.AddField(
            model_name='galeriafoto',
            name='external_image_url',
            field=models.URLField(blank=True, verbose_name='Imagen externa (URL)'),
        ),
        migrations.AlterField(
            model_name='galeriafoto',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='galeria/'),
        ),
    ]
