from django.urls import include

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views



urlpatterns = [
    path(r'auth/', include('djoser.urls.authtoken')),
]