from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers
from drf_base64.fields import Base64ImageField

from recipes.models import User, Tag, IngredientCount, Ingredient, Recipe, \
    Favorites, ShoppingCart
from users.models import Subscribe


class UserGetSerializer(UserSerializer):
    """[GET] Cписок пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
                and not self.context['request'].user.is_anonymous):
            return Subscribe.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        return False


class UserCreateSerializer(UserCreateSerializer):
    """[POST] Создание нового пользователя."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'password')
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
        }

    def validate(self, obj):
        invalid_usernames = ['me', 'set_password',
                             'subscriptions', 'subscribe']
        if self.initial_data.get('username') in invalid_usernames:
            raise serializers.ValidationError(
                {'username': 'Вы не можете использовать этот username.'}
            )
        return obj


class PasswordSerializer(serializers.Serializer):
    """[POST] Изменение пароля пользователя."""
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, obj):
        try:
            validate_password(obj['new_password'])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)}
            )
        return super().validate(obj)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Неправильный пароль.'}
            )
        if (validated_data['current_password']
                == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Для использования в подписках."""
    image = Base64ImageField()
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """[GET] Список авторов на которых подписан пользователь."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeShortSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
                and not self.context['request'].user.is_anonymous):
            return Subscribe.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    """Подписка на автора и отписка."""
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeShortSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
                and not self.context['request'].user.is_anonymous):
            return Subscribe.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """[GET] Список тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """[GET] Список ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Список ингредиенты и их количество."""
    id = serializers.ReadOnlyField(source=Ingredient.id)
    name = serializers.ReadOnlyField(source=Ingredient.name)
    measurement_unit = serializers.ReadOnlyField(
        source=Ingredient.measurement_unit
    )

    class Meta:
        model = IngredientCount
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeGetSerializer(serializers.ModelSerializer):
    """[GET] Рецепт(ы)."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserGetSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        return (
                self.context.get('request').user.is_authenticated
                and Favorites.objects.filter(user=self.context['request'].user,
                                             recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
                self.context.get('request').user.is_authenticated
                and ShoppingCart.objects.filter(
            user=self.context['request'].user,
            recipe=obj).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    pass
