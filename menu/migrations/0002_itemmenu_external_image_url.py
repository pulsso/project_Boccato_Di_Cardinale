# Generated manually for external menu images.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemmenu',
            name='external_image_url',
            field=models.URLField(blank=True, verbose_name='Imagen externa (URL)'),
        ),
    ]
