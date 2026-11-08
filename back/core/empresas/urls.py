from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DocumentoComprobatorioViewSet, EmpresaViewSet
from .views import EmpresaViewSet, EmpresaBuscaPublicaView

router = DefaultRouter()
router.register('empresas', EmpresaViewSet, basename='empresa')

urlpatterns = router.urls + [
    path(
        'empresas/<int:empresa_pk>/documentos/',
        DocumentoComprobatorioViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='empresa-documento-list',
    ),
    path(
        'empresas/<int:empresa_pk>/documentos/<int:pk>/',
        DocumentoComprobatorioViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
        name='empresa-documento-detail',
    ),
    path(
        'empresas/<int:empresa_pk>/documentos/<int:pk>/download/',
        DocumentoComprobatorioViewSet.as_view({'get': 'download'}),
        name='empresa-documento-download',
    ),
]
