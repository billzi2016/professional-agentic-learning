from django.contrib import admin
from django.urls import path

from apps.api_app.router import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
