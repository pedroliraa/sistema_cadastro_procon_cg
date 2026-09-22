from django.db import models


class AreaAtuacao(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class NivelSelo(models.Model):
    nome = models.CharField(max_length=20, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class Empresa(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('suspenso', 'Suspenso'),
        ('removido', 'Removido'),
    ]

    razao_social = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    endereco = models.CharField(max_length=255)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()

    areas = models.ManyToManyField(
        AreaAtuacao,
        related_name='empresas'
    )

    nivel_selo_atual = models.ForeignKey(
        NivelSelo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='empresas'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ativo'
    )

    def __str__(self):
        return self.razao_social


class HistoricoSelo(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='historico_selos'
    )

    nivel_selo = models.ForeignKey(
        NivelSelo,
        on_delete=models.PROTECT,
        related_name='historicos'
    )

    data_alteracao = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField(blank=True)

    def __str__(self):
        return f'{self.empresa} - {self.nivel_selo}'


class DocumentoComprobatorio(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='documentos'
    )

    arquivo = models.CharField(max_length=500)
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Documento - {self.empresa}'