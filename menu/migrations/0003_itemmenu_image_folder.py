# Generated manually for menu item image folders.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0002_itemmenu_external_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemmenu',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='menu/items/'),
        ),
    ]
