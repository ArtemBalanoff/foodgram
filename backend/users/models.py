from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import F, Q

from foodgram_backend.constants import NAME_MAX_LENGTH


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField('Эл. почта', unique=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/',
                               null=True, blank=True)
    first_name = models.CharField(
        'Имя', max_length=NAME_MAX_LENGTH, blank=False)
    last_name = models.CharField(
        'Фамилия', max_length=NAME_MAX_LENGTH, blank=False)
    subscriptions = models.ManyToManyField(
        'self', symmetrical=False, related_name='subscribers',
        verbose_name='Подписки', blank=True, through='Subscription')
    favorites = models.ManyToManyField(
        'recipes.Recipe', related_name='favorited_by', blank=True,
        verbose_name='Избранное', through='recipes.Favorite')
    shopping_cart = models.ManyToManyField(
        'recipes.Recipe', related_name='in_shopping_cart', blank=True,
        verbose_name='Корзина', through='recipes.ShoppingCart')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('is_staff', '-date_joined')

    def __str__(self):
        if self.is_staff:
            return self.email
        return (self.first_name + ' ' + self.last_name)

    @property
    def recipes_count(self):
        return self.recipes.count()

    @property
    def subs_count(self):
        return self.subscribers.count()


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Подписчик', related_name='+')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Автор', related_name='+')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.CheckConstraint(
                check=~Q(subscriber=F('author')),
                name='prevent_self_subscription'
            ),
            models.UniqueConstraint(
                fields=('subscriber', 'author'),
                name='unique_subscriber_author'
            )
        ]

    def __str__(self):
        return f'Подписка: {self.subscriber} - {self.author}'
