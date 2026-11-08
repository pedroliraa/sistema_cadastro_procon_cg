from django.urls import reverse
from rest_framework import serializers

from .models import DocumentoComprobatorio, Empresa


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


class DocumentoComprobatorioSerializer(serializers.ModelSerializer):
    url_download = serializers.SerializerMethodField()

    class Meta:
        model = DocumentoComprobatorio
        fields = ['id', 'arquivo', 'nome_original', 'enviado_por',
                  'data_upload', 'url_download']
        read_only_fields = ['id', 'nome_original', 'enviado_por',
                            'data_upload', 'url_download']
        # o arquivo só entra no upload; a saída é pelo endpoint de download
        extra_kwargs = {'arquivo': {'write_only': True}}

    def get_url_download(self, obj) -> str:
        return reverse(
            'empresa-documento-download',
            args=[obj.empresa_id, obj.pk],
        )
class EmpresaPublicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['id', 'razao_social']
        read_only_fields = ['id', 'razao_social']
