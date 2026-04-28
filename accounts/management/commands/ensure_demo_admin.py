import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crea o actualiza un superusuario de demo usando variables de entorno.'

    def handle(self, *args, **options):
        username = os.getenv('DEMO_ADMIN_USERNAME', '').strip()
        email = os.getenv('DEMO_ADMIN_EMAIL', '').strip()
        password = os.getenv('DEMO_ADMIN_PASSWORD', '').strip()

        if not username or not password:
            self.stdout.write('DEMO_ADMIN_USERNAME/DEMO_ADMIN_PASSWORD no definidos; se omite admin demo.')
            return

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
            },
        )

        user.email = email or user.email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = 'creado' if created else 'actualizado'
        self.stdout.write(self.style.SUCCESS(f'Superusuario demo {action}: {username}'))
