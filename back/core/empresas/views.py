from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from usuarios.permissions import IsAnalistaOuGestor, IsGestor

from . import services
from .models import AreaAtuacao, Empresa
from .serializers import (
    AreaAtuacaoSerializer,
    AlterarStatusSerializer,
    EmpresaPublicaSerializer,
    EmpresaSerializer,
    HistoricoStatusSerializer,
    RevalidarSerializer,
)
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

class EmpresaPagination(PageNumberPagination):

    page_size = 20

class AreaAtuacaoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AreaAtuacao.objects.all()
    serializer_class = AreaAtuacaoSerializer
    permission_classes = [IsAnalistaOuGestor]
    pagination_class = None

    
class EmpresaViewSet(viewsets.ModelViewSet):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = Empresa.objects.prefetch_related('areas')
    serializer_class = EmpresaSerializer
    pagination_class = EmpresaPagination

    def get_permissions(self):
        # só o gestor pode excluir
        if self.action == 'destroy':
            return [IsGestor()]
        # analista e gestor: listar, ver, criar e editar
        # (alterar-status tem uma checagem extra para "removido", ver abaixo)
        return [IsAnalistaOuGestor()]

    # ---------------- PB-11 ----------------

    @action(detail=True, methods=['post'], url_path='alterar-status')
    def alterar_status(self, request, pk=None):
        """Suspende, remove ou reativa a empresa (RN06). Motivo obrigatório.

        Body: {"status": "suspenso" | "removido" | "ativo", "motivo": "..."}
        """
        empresa = self.get_object()
        entrada = AlterarStatusSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        novo_status = entrada.validated_data['status']

        # Remover (ou tirar da remoção) segue a mesma regra do DELETE: só gestor
        if 'removido' in (empresa.status, novo_status):
            if not IsGestor().has_permission(request, self):
                raise PermissionDenied(
                    'Apenas o gestor pode remover ou reativar empresa removida.'
                )

        try:
            empresa, _ = services.alterar_status(
                empresa, novo_status, entrada.validated_data['motivo'], request.user
            )
        except services.StatusInvalido as erro:
            raise ValidationError({'status': [str(erro)]})

        return Response(self.get_serializer(empresa).data)

    @action(detail=True, methods=['post'])
    def revalidar(self, request, pk=None):
        """Registra a revalidação periódica (RN05) e renova o prazo.

        Body (opcional): {"motivo": "..."}
        """
        empresa = self.get_object()
        entrada = RevalidarSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)

        try:
            empresa, _ = services.revalidar(
                empresa, request.user, entrada.validated_data['motivo']
            )
        except services.StatusInvalido as erro:
            raise ValidationError({'status': [str(erro)]})

        return Response(self.get_serializer(empresa).data)

    @action(detail=True, methods=['get'], url_path='historico-status')
    def historico_status(self, request, pk=None):
        empresa = self.get_object()
        historico = empresa.historico_status.select_related('usuario')
        pagina = self.paginate_queryset(historico)
        serializer = HistoricoStatusSerializer(pagina, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='revalidacoes-vencidas')
    def revalidacoes_vencidas(self, request):
        """Empresas ativas ou suspensas com o prazo de revalidação vencido."""
        empresas = (
            services.empresas_com_revalidacao_vencida()
            .prefetch_related('areas')
            .order_by('data_proxima_revalidacao')
        )
        pagina = self.paginate_queryset(empresas)
        serializer = self.get_serializer(pagina, many=True)
        return self.get_paginated_response(serializer.data)


class EmpresaBuscaPublicaView(generics.ListAPIView):
    serializer_class = EmpresaPublicaSerializer
    permission_classes = [AllowAny]
    pagination_class = EmpresaPagination

    def get_queryset(self):
        nome = self.request.query_params.get('nome', '').strip()
        area = self.request.query_params.get('area', '').strip()

        if not nome and not area:
            return Empresa.objects.none()

        # suspensas e removidas não aparecem na consulta pública
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
