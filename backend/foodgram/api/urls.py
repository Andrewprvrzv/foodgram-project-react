from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, RecipeViewSet, SubscribeViewSet,
                    SubscriptionsViewSet, TagViewSet, UsersViewSet)

router = DefaultRouter()
router.register(r'users/subscriptions', SubscriptionsViewSet)
router.register(r'users', UsersViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path(r'users/<int:pk>/subscribe/', SubscribeViewSet.as_view({
        'post': 'retrieve',
        'delete': 'retrieve',
    })),
    path(r'auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
