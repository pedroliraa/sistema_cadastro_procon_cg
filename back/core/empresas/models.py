import calendar

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from .validators import validar_cnpj


def somar_meses(data, meses):
    """Soma meses a uma data, ajustando o dia ao fim do mês quando preciso
    (ex.: 31/08 + 6 meses = 28/02 ou 29/02)."""
    mes = data.month - 1 + meses
    ano = data.year + mes // 12
    mes = mes % 12 + 1
    dia = min(data.day, calendar.monthrange(ano, mes)[1])
    return data.replace(year=ano, month=mes, day=dia)


def calcular_proxima_revalidacao(data_base):
    # RN05: revalidação periódica. Proposta inicial semestral, a confirmar
    # pelo regulamento — por isso fica configurável em settings.
    meses = getattr(settings, 'REVALIDACAO_MESES', 6)
    return somar_meses(data_base, meses)


class AreaAtuacao(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Área de atuação"
        verbose_name_plural = "Áreas de atuação"
        ordering = ["nome"]

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
    cnpj = models.CharField(  # ALTERADO
        max_length=14,
        unique=True,
        validators=[validar_cnpj],
        help_text='14 caracteres, sem pontuação.',
    )
    endereco = models.CharField(max_length=255)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    telefone = models.CharField(  # ALTERADO
        max_length=11,
        validators=[RegexValidator(r'^\d{10,11}$', 'Telefone com 10 ou 11 dígitos, DDD incluso e sem pontuação.')],
    )
    email = models.EmailField()

    foto = models.ImageField(
    upload_to='empresas/',
    null=True,
    blank=True
)

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

    # PB-11: revalidação periódica
    data_ultima_validacao = models.DateField(null=True, blank=True)
    data_proxima_revalidacao = models.DateField(null=True, blank=True)

    class Meta:  # NOVO
        ordering = ['razao_social']

    def __str__(self):
        return self.razao_social

    def save(self, *args, **kwargs):
        # Empresa nova já nasce validada (RN03: o cadastro só é feito depois
        # da visita de verificação) e com o prazo da próxima revalidação.
        if self._state.adding and self.data_ultima_validacao is None:
            self.data_ultima_validacao = timezone.localdate()
        if self.data_ultima_validacao and self.data_proxima_revalidacao is None:
            self.data_proxima_revalidacao = calcular_proxima_revalidacao(
                self.data_ultima_validacao
            )
        super().save(*args, **kwargs)

    @property
    def revalidacao_vencida(self):
        if self.status == 'removido' or self.data_proxima_revalidacao is None:
            return False
        return self.data_proxima_revalidacao < timezone.localdate()


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

    selo_anterior = models.ForeignKey(
        NivelSelo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='+'
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alteracoes_selo_empresa'
    )

    data_alteracao = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Histórico de selo'
        verbose_name_plural = 'Históricos de selo'
        ordering = ['-data_alteracao', '-id']

    def __str__(self):
        return f'{self.empresa} - {self.nivel_selo}'


class HistoricoStatus(models.Model):
    """PB-11: registra cada mudança de status e cada revalidação."""

    TIPO_CHOICES = [
        ('alteracao', 'Alteração de status'),
        ('revalidacao', 'Revalidação'),
    ]

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='historico_status'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    status_anterior = models.CharField(max_length=20, choices=Empresa.STATUS_CHOICES)
    status_novo = models.CharField(max_length=20, choices=Empresa.STATUS_CHOICES)
    motivo = models.TextField(blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alteracoes_status_empresa'
    )
    data_alteracao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Histórico de status'
        verbose_name_plural = 'Históricos de status'
        ordering = ['-data_alteracao', '-id']

    def __str__(self):
        return f'{self.empresa} - {self.status_anterior} → {self.status_novo}'


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
