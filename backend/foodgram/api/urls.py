from django.urls import include, re_path

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


urlpatterns = [
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
