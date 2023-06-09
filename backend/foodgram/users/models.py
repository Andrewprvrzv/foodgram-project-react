from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from foodgram.settings import REGEX_VALID_USERNAME


class User(AbstractUser):
    username = models.CharField(
        max_length=254,
        blank=False,
        unique=True,
        validators=[
            RegexValidator(REGEX_VALID_USERNAME,
                           message='Недопустимое имя.')
        ]
    )
    email = models.EmailField(
        max_length=254,
        blank=False,
        unique=True,
        verbose_name='Адрес электронной почты',
        help_text='Введите свой электронный адрес'
    )
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ('username', 'first_name',
                       'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_username_email'
            ),
        )

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Подписан'
    )

    class Meta:
        verbose_name = 'Подписка на авторов'
        verbose_name_plural = 'Подписки на авторов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe'
            )
        ]
