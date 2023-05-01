from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, RecipeViewSet, SubscribeViewSet,
                    SubscriptionsViewSet, TagViewSet)

router = DefaultRouter()
router.register(r'users/subscriptions',
                SubscriptionsViewSet,
                basename='subscriptions-list')
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path(r'users/<int:pk>/subscribe/', SubscribeViewSet.as_view({
        'post': 'retrieve',
        'delete': 'retrieve',
    })),
    path(r'auth/', include('djoser.urls.authtoken')),
    path(r'', include('djoser.urls')),
    path('', include(router.urls)),
]
