from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from usuarios.permissions import IsAnalistaOuGestor, IsGestor

from .models import Empresa
from .serializers import EmpresaSerializer


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