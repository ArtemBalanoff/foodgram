from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    email = models.EmailField('Эл. почта', unique=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/',
                               null=True, blank=True)
    subscriptions = models.ManyToManyField(
        'self', symmetrical=False, related_name='subscribers',
        verbose_name='Подписки')
    favourites = models.ManyToManyField(
        'recipes.Recipe', related_name='lovers', verbose_name='Избранное')
    shopping_cart = models.ManyToManyField(
        'recipes.Recipe', related_name='+', verbose_name='Корзина')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name',
                       'password']
    objects = CustomUserManager()
