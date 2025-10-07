from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.tasks.api_urls")),  
    path("", include("apps.tasks.urls")),         
    path("", TemplateView.as_view(template_name="base.html")),
]
