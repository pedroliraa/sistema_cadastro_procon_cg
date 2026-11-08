import os
import re

from django.core.exceptions import ValidationError

PESOS_DV1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
PESOS_DV2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

EXTENSOES_PERMITIDAS = {'.pdf', '.jpg', '.jpeg', '.png'}
TAMANHO_MAXIMO = 5 * 1024 * 1024  # 5 MB

ASSINATURAS = {
    '.pdf': (b'%PDF-',),
    '.png': (b'\x89PNG\r\n\x1a\n',),
    '.jpg': (b'\xff\xd8\xff',),
    '.jpeg': (b'\xff\xd8\xff',),
}


def _digito_verificador(base, pesos):
    # Regra oficial: valor do caractere = código ASCII - 48
    # (para dígitos dá o próprio dígito; "A" vale 17, "B" vale 18...)
    soma = sum((ord(c) - 48) * peso for c, peso in zip(base, pesos))
    resto = soma % 11
    return '0' if resto < 2 else str(11 - resto)


def validar_cnpj(valor):
    if not re.fullmatch(r'[0-9A-Z]{12}[0-9]{2}', valor):
        raise ValidationError(
            'O CNPJ deve ter 14 caracteres, sem pontuação: 12 letras maiúsculas '
            'ou números seguidos de 2 dígitos verificadores.'
        )
    if len(set(valor)) == 1:  # ex.: 00000000000000
        raise ValidationError('CNPJ inválido.')
    dv1 = _digito_verificador(valor[:12], PESOS_DV1)
    dv2 = _digito_verificador(valor[:12] + dv1, PESOS_DV2)
    if valor[12:] != dv1 + dv2:
        raise ValidationError('CNPJ inválido: os dígitos verificadores não conferem.')


def validar_documento(arquivo):
    """PB-09: aceita só PDF, JPG e PNG, até 5 MB, e confere o conteúdo real."""
    extensao = os.path.splitext(arquivo.name)[1].lower()
    if extensao not in EXTENSOES_PERMITIDAS:
        raise ValidationError('Envie um arquivo PDF, JPG ou PNG.')
    if arquivo.size > TAMANHO_MAXIMO:
        raise ValidationError('O arquivo deve ter no máximo 5 MB.')
    cabecalho = arquivo.read(8)
    arquivo.seek(0)
    if not cabecalho.startswith(ASSINATURAS[extensao]):
        raise ValidationError('O conteúdo do arquivo não corresponde à extensão.')