from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.pagination import CustomPaginator
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (IngredientSerializer, RecipeCreateSerializer,
                             RecipeGetSerializer, RecipeShortSerializer,
                             SubscribeSerializer, TagSerializer)
from foodgram.settings import FILE
from recipes.models import (Favorites, Ingredient, IngredientCount, Recipe,
                            ShoppingCart, Tag, User)
from users.models import Subscribe
from users.serializers import PasswordSerializer, UserViewSerializer


class UsersViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserViewSerializer

    def perform_create(self, serializer):
        if "password" in self.request.data:
            serializer.save(password=self.request.data["password"])
        else:
            serializer.save()

    def perform_update(self, serializer):
        if "password" in self.request.data:
            password = make_password(self.request.data["password"])
            serializer.save(password=password)
        else:
            serializer.save()

    @action(methods=["get"],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = UserViewSerializer(user)
        return Response(serializer.data)

    @action(detail=False,
            methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = PasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = SubscribeSerializer
    pagination_class = CustomPaginator
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get',)

    def get_queryset(self):
        return User.objects.filter(subscribing__user=self.request.user)


class SubscribeViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author, data=request.data, context={"request": request})
            if request.user == author:
                return Response({'detail': 'Ошибка подписки'},
                                status=status.HTTP_400_BAD_REQUEST)
            if Subscribe.objects.filter(user=request.user,
                                        author=author).exists():
                return Response({'detail': 'Вы уже подписаны'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Subscribe, user=request.user,
                              author=author).delete()
            return Response({'detail': 'Успешная отписка'},
                            status=status.HTTP_204_NO_CONTENT)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'create', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])

        if request.method == 'POST':
            serializer = RecipeShortSerializer(recipe,
                                               data=request.data,
                                               context={"request": request})
            serializer.is_valid(raise_exception=True)
            if Favorites.objects.filter(user=request.user,
                                        recipe=recipe).exists():
                return Response({'detail': 'Рецепт уже в избранном!'},
                                status=status.HTTP_400_BAD_REQUEST)
            Favorites.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Favorites.objects.filter(user=request.user,
                                            recipe=recipe).exists():
                return Response({'detail': 'Рецепта не было в избранном!'
                                           'Нечего удалять!'},
                                status=status.HTTP_400_BAD_REQUEST)
            Favorites.objects.filter(user=request.user,
                                     recipe=recipe).delete()
            return Response({'detail': 'Рецепт успешно удален из избранного.'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])

        if request.method == 'POST':
            serializer = RecipeShortSerializer(recipe,
                                               data=request.data,
                                               context={"request": request})
            serializer.is_valid(raise_exception=True)
            if ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                return Response({'detail': 'Рецепт уже в списке покупок!'},
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not ShoppingCart.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                return Response({'detail': 'Рецепта нет в списке покупок!'},
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.filter(user=request.user,
                                        recipe=recipe).delete()
            return Response({'detail': 'Рецепт успешно удален из списка '
                                       'покупок.'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            IngredientCount.objects
            .filter(recipe__shopping_list__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
            .order_by('ingredient__name')
        )
        file_list = []
        [file_list.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
        file = HttpResponse('Чтобы поесть купите'
                            ' следующие продукты:\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = f'attachment; filename={FILE}'
        return file
