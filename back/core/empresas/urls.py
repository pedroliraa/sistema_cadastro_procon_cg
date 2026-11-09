from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import EmpresaViewSet, EmpresaBuscaPublicaView, AreaAtuacaoViewSet

router = DefaultRouter()
router.register('empresas', EmpresaViewSet, basename='empresa')
router.register('areas', AreaAtuacaoViewSet, basename='area')

urlpatterns = [
    path(
        'publico/empresas/',
        EmpresaBuscaPublicaView.as_view(),
        name='empresa-busca-publica',
    ),
] + router.urls