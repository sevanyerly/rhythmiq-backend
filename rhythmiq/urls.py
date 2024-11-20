"""
URL configuration for rhythmiq project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, re_path, include
from app_rhythmiq.views.swagger import schema_view
from knox import views as knox_views
import app_rhythmiq.views as rhythmiq_views

from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r"downloadedSong", rhythmiq_views.DownloadedSongViewSet)
router.register(r"signup", rhythmiq_views.SignUpViewSet, basename="signup")
router.register(r"songs", rhythmiq_views.SongViewSet, basename="song")

urlpatterns = [
    path("admin/", admin.site.urls),
    path(r"api/auth/", include("knox.urls")),
    path(r"api/auth/user/", rhythmiq_views.UserView.as_view(), name="user_info"),
    path(r"api/login/", rhythmiq_views.LoginView.as_view(), name="knox_login"),
    path(r"api/logout/", rhythmiq_views.LogoutView.as_view(), name="knox_logout"),
    path(r"api/logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
    path("api/", include(router.urls)),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
