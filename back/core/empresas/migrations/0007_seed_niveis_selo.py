from django.db import migrations

SELOS = ['Qualificado', 'Confiável', 'Excelência', 'Referência']


def criar_selos(apps, schema_editor):
    NivelSelo = apps.get_model('empresas', 'NivelSelo')
    for nome in SELOS:
        NivelSelo.objects.get_or_create(nome=nome)


class Migration(migrations.Migration):

    dependencies = [
        ('empresas', '0006_historico_selo_usuario'),
    ]

    operations = [
        migrations.RunPython(criar_selos, migrations.RunPython.noop),
    ]
