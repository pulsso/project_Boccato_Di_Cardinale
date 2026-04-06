from django.contrib.auth.models import User
from django.db import models

from config.commerce import SECTOR_CHOICES, ZONE_CHOICES


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    zone = models.CharField(max_length=20, choices=ZONE_CHOICES, blank=True)
    sector = models.CharField(max_length=30, choices=SECTOR_CHOICES, blank=True)
    default_address = models.TextField(blank=True)
    mobile_phone = models.CharField(max_length=20, blank=True)
    landline_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil cliente'
        verbose_name_plural = 'Perfiles cliente'

    def __str__(self):
        return f'Perfil {self.user.username}'
