from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.conf import settings
from core.views import homepage

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("", homepage),
    path("", include("authentication_app.urls")),
    path("", include("newsportal.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

admin.site.site_title = "AbiralSanchar"
admin.site.site_header = "AbiralSanchar - ADMIN"
admin.site.index_title = "AbiralSanchar"
