# tasker/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.tasks.api_urls")),  # DRF для бота/фронта
    path("", include("apps.tasks.urls")),          # пользовательские страницы
    # опционально: запасная домашняя (если попадут на "/")
    path("", TemplateView.as_view(template_name="base.html")),
]
