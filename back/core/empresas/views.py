from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .models import Empresa
from .serializers import EmpresaSerializer


class EmpresaPagination(PageNumberPagination):
    page_size = 20


class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.prefetch_related('areas')
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = EmpresaPagination
