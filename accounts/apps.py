from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        import os

        if os.getenv('VERCEL', '').strip() != '1':
            return

        if os.getenv('DATABASE_URL', '').strip():
            return

        from django.contrib.auth.models import update_last_login
        from django.contrib.auth.signals import user_logged_in

        user_logged_in.disconnect(update_last_login)
