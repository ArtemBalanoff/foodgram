from django.db import models
from django.contrib.auth.models import AbstractUser


class Customer(AbstractUser):
    avatar = models.ImageField('Аватар', upload_to='avatars/',
                               null=True, blank=True)
