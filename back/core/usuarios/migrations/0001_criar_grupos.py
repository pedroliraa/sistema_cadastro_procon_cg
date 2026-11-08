from django.db import migrations


def criar_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for nome in ("Analista", "Gestor"):
        Group.objects.get_or_create(name=nome)


class Migration(migrations.Migration):
    dependencies = [("auth", "0012_alter_user_first_name_max_length")]
    operations = [migrations.RunPython(criar_grupos, migrations.RunPython.noop)]