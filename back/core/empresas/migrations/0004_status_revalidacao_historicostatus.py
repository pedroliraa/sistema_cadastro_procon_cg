import calendar

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


def preencher_datas_existentes(apps, schema_editor):
    """Empresas já cadastradas antes da PB-11 ganham a data de hoje como
    última validação, com o prazo a partir de hoje."""
    Empresa = apps.get_model('empresas', 'Empresa')
    meses = getattr(settings, 'REVALIDACAO_MESES', 6)

    hoje = timezone.localdate()
    mes = hoje.month - 1 + meses
    ano = hoje.year + mes // 12
    mes = mes % 12 + 1
    dia = min(hoje.day, calendar.monthrange(ano, mes)[1])
    proxima = hoje.replace(year=ano, month=mes, day=dia)

    Empresa.objects.filter(data_ultima_validacao__isnull=True).update(
        data_ultima_validacao=hoje,
        data_proxima_revalidacao=proxima,
    )


STATUS_CHOICES = [('ativo', 'Ativo'), ('suspenso', 'Suspenso'), ('removido', 'Removido')]


class Migration(migrations.Migration):

    dependencies = [
        ('empresas', '0003_alter_areaatuacao_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='empresa',
            name='data_ultima_validacao',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='empresa',
            name='data_proxima_revalidacao',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='HistoricoStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('alteracao', 'Alteração de status'), ('revalidacao', 'Revalidação')], max_length=20)),
                ('status_anterior', models.CharField(choices=STATUS_CHOICES, max_length=20)),
                ('status_novo', models.CharField(choices=STATUS_CHOICES, max_length=20)),
                ('motivo', models.TextField(blank=True)),
                ('data_alteracao', models.DateTimeField(auto_now_add=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historico_status', to='empresas.empresa')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alteracoes_status_empresa', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Histórico de status',
                'verbose_name_plural': 'Históricos de status',
                'ordering': ['-data_alteracao', '-id'],
            },
        ),
        migrations.RunPython(preencher_datas_existentes, migrations.RunPython.noop),
    ]
