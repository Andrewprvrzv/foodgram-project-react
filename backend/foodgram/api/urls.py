from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UsersViewSet, TagViewSet, IngredientsViewSet

router = DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientsViewSet)

urlpatterns = [
    path(r'auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
