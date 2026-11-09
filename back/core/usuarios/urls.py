from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import MeView, UsuarioViewSet

router = DefaultRouter()
router.register("usuarios", UsuarioViewSet, basename="usuario")

urlpatterns = [
    # POST {"username", "password"} → {"token": "..."}
    path("auth/login/", obtain_auth_token, name="auth-login"),
    path("auth/me/", MeView.as_view()),
    path("", include(router.urls)),
]
