from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=254,
        blank=False,
        unique=True,
        validators=[
            RegexValidator('^[\w.@+-]+\z',
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
