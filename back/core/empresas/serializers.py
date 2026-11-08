from rest_framework import serializers

from .models import Empresa


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = [
            'id', 'razao_social', 'cnpj',
            'endereco', 'bairro', 'cidade',
            'telefone', 'email',
            'areas', 'nivel_selo_atual', 'status',
        ]
        # Selo e status têm regras próprias (PB-10 e PB-11), então não se
        # alteram pelo CRUD básico.
        read_only_fields = ['id', 'nivel_selo_atual', 'status']

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