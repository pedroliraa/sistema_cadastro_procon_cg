from django.dispatch import Signal

# PB-11 → PB-12
# Disparado (após o commit da transação) sempre que o status de uma empresa
# muda. A notificação por e-mail da PB-12 só precisa se conectar aqui, ex.:
#
#     from django.dispatch import receiver
#     from empresas.signals import status_alterado
#
#     @receiver(status_alterado)
#     def notificar_empresa(sender, empresa, status_anterior, status_novo,
#                           motivo, usuario, **kwargs):
#         ...
#
# Argumentos enviados: empresa, status_anterior, status_novo, motivo, usuario
status_alterado = Signal()
