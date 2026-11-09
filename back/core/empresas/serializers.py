from rest_framework import serializers
from django.db import transaction

from . import services

from .models import AreaAtuacao, Empresa, HistoricoSelo, HistoricoStatus, NivelSelo


class AreaAtuacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaAtuacao
        fields = ['id', 'nome']
        read_only_fields = fields


class NivelSeloSerializer(serializers.ModelSerializer):
    class Meta:
        model = NivelSelo
        fields = ['id', 'nome', 'descricao']
        read_only_fields = fields


class EmpresaSerializer(serializers.ModelSerializer):
    revalidacao_vencida = serializers.BooleanField(read_only=True)
    selo = serializers.CharField(
        source='nivel_selo_atual.nome', read_only=True, allow_null=True
    )
    # Escolha opcional do selo no cadastro/edição (só escrita)
    nivel_selo = serializers.PrimaryKeyRelatedField(
        queryset=NivelSelo.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Empresa
        fields = [
            'id', 'razao_social', 'cnpj',
            'endereco', 'bairro', 'cidade',
            'telefone', 'email', 'foto',
            'areas', 'nivel_selo_atual', 'selo', 'nivel_selo', 'status',
            'data_ultima_validacao', 'data_proxima_revalidacao',
            'revalidacao_vencida',
        ]
        read_only_fields = [
            'id', 'nivel_selo_atual', 'selo', 'status',
            'data_ultima_validacao', 'data_proxima_revalidacao',
        ]

    def _aplicar_selo(self, empresa, nivel, motivo):
        if nivel and empresa.nivel_selo_atual_id != nivel.pk:
            usuario = self.context['request'].user
            services.alterar_selo(empresa, nivel, motivo, usuario)
            empresa.refresh_from_db()
        return empresa

    def create(self, validated_data):
        nivel = validated_data.pop('nivel_selo', None)
        with transaction.atomic():
            empresa = super().create(validated_data)
            return self._aplicar_selo(empresa, nivel, 'Selo definido no cadastro')

    def update(self, instance, validated_data):
        nivel = validated_data.pop('nivel_selo', None)
        with transaction.atomic():
            empresa = super().update(instance, validated_data)
            return self._aplicar_selo(empresa, nivel, 'Selo alterado na edição')


class EmpresaPublicaSerializer(serializers.ModelSerializer):
    selo = serializers.CharField(
        source='nivel_selo_atual.nome', read_only=True, allow_null=True
    )
    areas = AreaAtuacaoSerializer(many=True, read_only=True)

    class Meta:
        model = Empresa
        fields = [
            'id', 'razao_social', 'foto',
            'endereco', 'bairro', 'cidade',
            'areas', 'selo',
        ]
        read_only_fields = fields


# Selo

class AlterarSeloSerializer(serializers.Serializer):
    nivel_selo = serializers.PrimaryKeyRelatedField(queryset=NivelSelo.objects.all())
    motivo = serializers.CharField(required=False, allow_blank=True, default='')


class HistoricoSeloSerializer(serializers.ModelSerializer):
    nivel_selo = serializers.CharField(source='nivel_selo.nome', read_only=True)
    selo_anterior = serializers.CharField(
        source='selo_anterior.nome', read_only=True, allow_null=True
    )
    usuario = serializers.CharField(
        source='usuario.username', read_only=True, allow_null=True
    )

    class Meta:
        model = HistoricoSelo
        fields = [
            'id', 'nivel_selo', 'selo_anterior',
            'motivo', 'usuario', 'data_alteracao',
        ]
        read_only_fields = fields


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
