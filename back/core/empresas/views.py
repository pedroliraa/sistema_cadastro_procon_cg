from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from usuarios.permissions import IsAnalistaOuGestor, IsGestor

from .models import Empresa
from .serializers import EmpresaSerializer

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

class EmpresaBuscaPublicaView(generics.ListAPIView):
    serializer_class = EmpresaPublicaSerializer
    permission_classes = [AllowAny]
    pagination_class = EmpresaPagination

    def get_queryset(self):
        nome = self.request.query_params.get('nome', '').strip()
        area = self.request.query_params.get('area', '').strip()

        if not nome and not area:
            return Empresa.objects.none()

        empresas = Empresa.objects.filter(status='ativo')

        if nome:
            empresas = empresas.filter(
                razao_social__icontains=nome
            )

        if area:
            empresas = empresas.filter(
                areas__nome__icontains=area
            )

        return empresas.distinct().order_by('razao_social')
