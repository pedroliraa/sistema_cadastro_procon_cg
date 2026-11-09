from rest_framework import serializers

from .models import AreaAtuacao, Empresa, HistoricoStatus

class AreaAtuacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaAtuacao
        fields = ['id', 'nome']
        read_only_fields = fields

class EmpresaSerializer(serializers.ModelSerializer):
    revalidacao_vencida = serializers.BooleanField(read_only=True)

    class Meta:
        model = Empresa
        fields = [
            'id', 'razao_social', 'cnpj',
            'endereco', 'bairro', 'cidade',
            'telefone', 'email', 'foto',
            'areas', 'nivel_selo_atual', 'status',
            'data_ultima_validacao', 'data_proxima_revalidacao',
            'revalidacao_vencida',
        ]
        # Selo e status têm regras próprias (PB-10 e PB-11), então não se
        # alteram pelo CRUD básico. Status e revalidação mudam pelas ações
        # alterar-status/ e revalidar/ (ver EmpresaViewSet).
        read_only_fields = [
            'id', 'nivel_selo_atual', 'status',
            'data_ultima_validacao', 'data_proxima_revalidacao',
        ]


class EmpresaPublicaSerializer(serializers.ModelSerializer):
    selo = serializers.CharField(
        source='nivel_selo_atual.nome',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Empresa
        fields = ['id', 'razao_social', 'selo']
        read_only_fields = ['id', 'razao_social', 'selo']


# PB-11

class AlterarStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Empresa.STATUS_CHOICES)
    motivo = serializers.CharField(allow_blank=False, trim_whitespace=True)


class RevalidarSerializer(serializers.Serializer):
    motivo = serializers.CharField(required=False, allow_blank=True, default='')


class HistoricoStatusSerializer(serializers.ModelSerializer):
    usuario = serializers.CharField(
        source='usuario.username', read_only=True, allow_null=True
    )

    class Meta:
        model = HistoricoStatus
        fields = [
            'id', 'tipo', 'status_anterior', 'status_novo',
            'motivo', 'usuario', 'data_alteracao',
        ]
        read_only_fields = fields
