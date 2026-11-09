from django.core.management.base import BaseCommand

from empresas import services


class Command(BaseCommand):
    help = (
        'PB-11: lista as empresas com revalidação vencida. '
        'Com --suspender, suspende as que ainda estão ativas.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--suspender',
            action='store_true',
            help='Suspende automaticamente as empresas ativas com prazo vencido.',
        )

    def handle(self, *args, **options):
        vencidas = list(
            services.empresas_com_revalidacao_vencida().order_by('data_proxima_revalidacao')
        )

        if not vencidas:
            self.stdout.write(self.style.SUCCESS('Nenhuma revalidação vencida.'))
            return

        self.stdout.write(f'{len(vencidas)} empresa(s) com revalidação vencida:')
        for empresa in vencidas:
            self.stdout.write(
                f'  - {empresa.razao_social} ({empresa.cnpj}) | status: {empresa.status} '
                f'| venceu em {empresa.data_proxima_revalidacao:%d/%m/%Y}'
            )

        if options['suspender']:
            suspensas = services.suspender_vencidas()
            self.stdout.write(self.style.WARNING(f'{len(suspensas)} empresa(s) suspensa(s).'))
