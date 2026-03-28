# company/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Company(models.Model):
    name        = models.CharField(max_length=150)
    slogan      = models.CharField(max_length=255, blank=True, help_text="Frase corta que aparece debajo del nombre")

    logo       = models.ImageField(upload_to="company/logo/", null=True, blank=True)
    logo_small = models.ImageField(upload_to="company/logo/", null=True, blank=True)

    primary_color    = models.CharField(max_length=7, default="#303854")
    secondary_color  = models.CharField(max_length=7, default="#C2CDD5")
    background_color = models.CharField(max_length=7, default="#F6F3EA")

    phone    = models.CharField(max_length=20, blank=True)
    email    = models.EmailField(blank=True)
    address  = models.TextField(blank=True)
    website  = models.URLField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)

    facebook  = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    tiktok    = models.URLField(blank=True)

    def __str__(self):
        return self.name

    @property
    def favicon_url(self):
        if self.logo_small:
            return self.logo_small.url
        if self.logo:
            return self.logo.url
        return None

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresa"


class User(AbstractUser):
    profile_photo = models.ImageField(upload_to="users/photos/", null=True, blank=True)
    phone         = models.CharField(max_length=20, blank=True)
    is_operador   = models.BooleanField(default=False)


class GoogleCalendarToken(models.Model):
    user          = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token  = models.TextField()
    refresh_token = models.TextField()
    token_expiry  = models.DateTimeField(null=True)

    def to_credentials(self):
        from google.oauth2.credentials import Credentials
        return Credentials(
            token=self.access_token,
            refresh_token=self.refresh_token,
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
        )