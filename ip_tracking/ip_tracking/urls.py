from django.urls import path, include, re_path
from .views import login_view
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="IP Tracking API",
        default_version="v1",
        description="API documentation for IP tracking and security system",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("admin/", admin.site.urls),
    path("ip_tracking/", include("ip_tracking.urls")),
    re_path(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
]
