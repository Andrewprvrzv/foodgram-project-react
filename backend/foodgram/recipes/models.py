from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models

from api.validators import validate_nonzero

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Тэг',
        help_text='Назначьте тэг'
    )
    color = models.CharField(
        max_length=7,
        null=True,
        verbose_name='Цвет тэга',
        help_text='Выберите цвет тэга',
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Поле должно содержать HEX-код выбранного цвета.'
            )
        ]
    )
    slug = models.CharField(
        max_length=200,
        verbose_name='Слаг тэга',
        help_text='Slug тэга',
        validators=[
            RegexValidator(
                '^[\w.@+-]+\z',
                message='Недопустимое имя.')
        ],
        unique=True
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование ингредиента',
        help_text='Выберите ингредиент'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        help_text='Единица измерения',
        max_length=200,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Автор рецепта'
    )
    name = models.CharField(
        max_length=200,
    )
    image = models.ImageField(
        upload_to='images/',
        blank=True,
        verbose_name='Картинка',
    )
    text = models.TextField(
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


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]


class IngredientCount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    name = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[validate_nonzero, ]
    )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'