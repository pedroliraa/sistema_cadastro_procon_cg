import re

from django.core.exceptions import ValidationError

PESOS_DV1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
PESOS_DV2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]


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
