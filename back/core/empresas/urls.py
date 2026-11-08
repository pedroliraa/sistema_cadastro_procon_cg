from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import EmpresaViewSet, EmpresaBuscaPublicaView

router = DefaultRouter()
router.register('empresas', EmpresaViewSet, basename='empresa')

urlpatterns = [
    path(
        'publico/empresas/',
        EmpresaBuscaPublicaView.as_view(),
        name='empresa-busca-publica',
    ),
] + router.urls