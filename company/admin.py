from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Company, User

admin.site.register(Company)
admin.site.register(User)