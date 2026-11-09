"""Regras de negócio da PB-11 (RN05 e RN06).

Toda mudança de status passa por aqui, para que o histórico seja sempre
gravado e o signal da PB-12 seja sempre disparado — seja pela API, seja
pelo comando de verificação de revalidações.
"""
from django.db import transaction
from django.utils import timezone

from .models import Empresa, HistoricoSelo, HistoricoStatus, calcular_proxima_revalidacao
from .signals import status_alterado

# Transições permitidas a partir de cada status
TRANSICOES = {
    'ativo': {'suspenso', 'removido'},
    'suspenso': {'ativo', 'removido'},
    'removido': {'ativo'},  # reativação (a view exige perfil Gestor)
}


class StatusInvalido(Exception):
    """Transição de status que a regra de negócio não permite."""


def alterar_status(empresa, novo_status, motivo, usuario=None):
    status_validos = dict(Empresa.STATUS_CHOICES)
    if novo_status not in status_validos:
        raise StatusInvalido(f'Status "{novo_status}" não existe.')

    motivo = (motivo or '').strip()
    if not motivo:
        raise StatusInvalido('Informe o motivo da alteração de status.')

    with transaction.atomic():
        # trava a linha para evitar duas alterações simultâneas
        empresa = Empresa.objects.select_for_update().get(pk=empresa.pk)
        status_anterior = empresa.status

        if novo_status == status_anterior:
            raise StatusInvalido(f'A empresa já está com status "{novo_status}".')
        if novo_status not in TRANSICOES[status_anterior]:
            raise StatusInvalido(
                f'Não é permitido mudar de "{status_anterior}" para "{novo_status}".'
            )

        empresa.status = novo_status
        empresa.save(update_fields=['status'])

        historico = HistoricoStatus.objects.create(
            empresa=empresa,
            tipo='alteracao',
            status_anterior=status_anterior,
            status_novo=novo_status,
            motivo=motivo,
            usuario=usuario,
        )

        # só avisa (PB-12) se a transação realmente for gravada
        transaction.on_commit(lambda: status_alterado.send(
            sender=Empresa,
            empresa=empresa,
            status_anterior=status_anterior,
            status_novo=novo_status,
            motivo=motivo,
            usuario=usuario,
        ))

    return empresa, historico


def revalidar(empresa, usuario=None, motivo=''):
    """Renova o prazo de revalidação. Não muda o status: uma empresa
    suspensa continua suspensa até alguém reativá-la explicitamente."""
    with transaction.atomic():
        empresa = Empresa.objects.select_for_update().get(pk=empresa.pk)

        if empresa.status == 'removido':
            raise StatusInvalido(
                'Empresa removida não pode ser revalidada. Reative-a primeiro.'
            )

        hoje = timezone.localdate()
        empresa.data_ultima_validacao = hoje
        empresa.data_proxima_revalidacao = calcular_proxima_revalidacao(hoje)
        empresa.save(update_fields=['data_ultima_validacao', 'data_proxima_revalidacao'])

        historico = HistoricoStatus.objects.create(
            empresa=empresa,
            tipo='revalidacao',
            status_anterior=empresa.status,
            status_novo=empresa.status,
            motivo=(motivo or '').strip() or 'Revalidação periódica',
            usuario=usuario,
        )

    return empresa, historico


def empresas_com_revalidacao_vencida():
    return Empresa.objects.filter(
        status__in=['ativo', 'suspenso'],
        data_proxima_revalidacao__lt=timezone.localdate(),
    )


def suspender_vencidas(usuario=None):
    """Suspende as empresas ativas com revalidação vencida. Retorna a lista."""
    suspensas = []
    for empresa in empresas_com_revalidacao_vencida().filter(status='ativo'):
        motivo = (
            'Suspensão automática: revalidação vencida em '
            f'{empresa.data_proxima_revalidacao:%d/%m/%Y}.'
        )
        empresa, _ = alterar_status(empresa, 'suspenso', motivo, usuario)
        suspensas.append(empresa)
    return suspensas

class SeloInvalido(Exception):
    """Troca de selo que a regra de negócio não permite."""


def alterar_selo(empresa, nivel_selo, motivo='', usuario=None):
    """Define manualmente o selo da empresa e grava no histórico."""
    with transaction.atomic():
        empresa = Empresa.objects.select_for_update().get(pk=empresa.pk)
        selo_anterior = empresa.nivel_selo_atual

        if selo_anterior and selo_anterior.pk == nivel_selo.pk:
            raise SeloInvalido(f'A empresa já possui o selo "{nivel_selo.nome}".')

        empresa.nivel_selo_atual = nivel_selo
        empresa.save(update_fields=['nivel_selo_atual'])

        historico = HistoricoSelo.objects.create(
            empresa=empresa,
            nivel_selo=nivel_selo,
            selo_anterior=selo_anterior,
            motivo=(motivo or '').strip(),
            usuario=usuario,
        )

    return empresa, historico
