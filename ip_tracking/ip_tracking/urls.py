from django.urls import path, include
from .views import login_view

urlpatterns = [
    path("login/", login_view, name="login"),
    path("admin/", admin.site.urls),
    path("ip_tracking/", include("ip_tracking.urls")),
]
