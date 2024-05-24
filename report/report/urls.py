from django.contrib import admin
from django.urls import path
from home.views import Home
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", Home),
]
