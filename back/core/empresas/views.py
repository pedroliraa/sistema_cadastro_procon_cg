from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

from usuarios.permissions import IsAnalistaOuGestor, IsGestor

from .models import DocumentoComprobatorio, Empresa
from .serializers import DocumentoComprobatorioSerializer, EmpresaSerializer

from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import EmpresaPublicaSerializer
class EmpresaPagination(PageNumberPagination):

    page_size = 20


class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.prefetch_related('areas')
    serializer_class = EmpresaSerializer
    pagination_class = EmpresaPagination

    def get_permissions(self):
        # só o gestor pode excluir
        if self.action == 'destroy':
            return [IsGestor()]
        # analista e gestor: listar, ver, criar e editar
        return [IsAnalistaOuGestor()]


class DocumentoComprobatorioViewSet(viewsets.ModelViewSet):
    """Documentos de uma empresa: /api/empresas/<empresa_pk>/documentos/"""
    serializer_class = DocumentoComprobatorioSerializer
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_permissions(self):
        # analista e gestor enviam e consultam; só o gestor exclui
        if self.action == 'destroy':
            return [IsGestor()]
        return [IsAnalistaOuGestor()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return DocumentoComprobatorio.objects.none()
        return DocumentoComprobatorio.objects.filter(
            empresa_id=self.kwargs['empresa_pk']
        ).order_by('-data_upload', '-id')

    def perform_create(self, serializer):
        empresa = get_object_or_404(Empresa, pk=self.kwargs['empresa_pk'])
        arquivo = serializer.validated_data['arquivo']
        serializer.save(
            empresa=empresa,
            enviado_por=self.request.user,
            nome_original=arquivo.name[:255],
        )

    def perform_destroy(self, instance):
        instance.arquivo.delete(save=False)  # apaga o arquivo do disco
        instance.delete()

    @extend_schema(responses={(200, 'application/octet-stream'): OpenApiTypes.BINARY})
    def download(self, request, empresa_pk=None, pk=None):
        documento = self.get_object()
        try:
            return FileResponse(
                documento.arquivo.open('rb'),
                as_attachment=True,
                filename=documento.nome_original or 'documento',
            )
        except FileNotFoundError:
            raise Http404
    def download(self, request, empresa_pk=None, pk=None):
        documento = self.get_object()
        try:
            return FileResponse(
                documento.arquivo.open('rb'),
                as_attachment=True,
                filename=documento.nome_original or 'documento',
            )
        except FileNotFoundError:
            raise Http404
