from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models

from backend.foodgram.api.validators import validate_nonzero

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Автор рецепта'
    )
    name = models.CharField(
        max_length=200,
    )
    image = models.ImageField(upload_to='images/')
    text = models.TextField(
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Описание рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время',
        help_text='Время приготовления в минутах',
        validators=[validate_nonzero, ]
    )
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(Ingredient)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        null=True,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Поле должно содержать HEX-код выбранного цвета.'
            )
        ]
    )
    slug = models.CharField(
        max_length=200,
        validators=[
            RegexValidator(
                '^[\w.@+-]+\z',
                message='Недопустимое имя.')
        ],
        unique=True
    )

    def __str__(self):
        return self.name
