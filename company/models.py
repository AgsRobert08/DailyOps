from django.db import models

class Company(models.Model):

    name = models.CharField(max_length=150)

    logo = models.ImageField(
        upload_to="company/logo/",
        null=True,
        blank=True
    )

    primary_color = models.CharField(
        max_length=7,
        default="#303854"
    )

    secondary_color = models.CharField(
        max_length=7,
        default="#C2CDD5"
    )

    background_color = models.CharField(
        max_length=7,
        default="#F6F3EA"
    )

    phone = models.CharField(max_length=20, blank=True)

    email = models.EmailField(blank=True)

    address = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    profile_photo = models.ImageField(
        upload_to="users/photos/",
        null=True,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )
    is_operador   = models.BooleanField(default=False) 