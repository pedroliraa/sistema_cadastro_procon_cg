# Dados de teste para desenvolvimento local. NÃO COMMITAR.
# Rodar (em back/core, com o venv ativo):
#   python manage.py shell -c "exec(open('seed_dev.py', encoding='utf-8').read())"
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

from empresas import services
from empresas.models import AreaAtuacao, Empresa, NivelSelo

User = get_user_model()

# --- usuários ---
gestor, criado = User.objects.get_or_create(
    username='gestor', defaults={'is_staff': True, 'is_superuser': True}
)
if criado:
    gestor.set_password('gestor123')
    gestor.save()
gestor.groups.add(Group.objects.get(name='Gestor'))

analista, criado = User.objects.get_or_create(username='analista')
if criado:
    analista.set_password('analista123')
    analista.save()
analista.groups.add(Group.objects.get(name='Analista'))

# --- áreas (mesmas dos botões da consulta pública) ---
areas = {
    nome: AreaAtuacao.objects.get_or_create(nome=nome)[0]
    for nome in ['Tecnologias', 'Moda', 'Casa', 'Alimentação', 'Saúde']
}

# --- selos (nomes das imagens em front/public/assets) ---
selos = {
    nome: NivelSelo.objects.get_or_create(nome=nome)[0]
    for nome in ['Referência', 'Excelência', 'Qualificado', 'Confiável']
}

# --- empresas ---
empresas = [
    # razão social, cnpj, áreas, selo
    ('Mercadinho Boa Compra LTDA', '11222333000181', ['Alimentação'], 'Referência'),
    ('TechNordeste Soluções LTDA', '22333444000181', ['Tecnologias'], 'Excelência'),
    ('Moda Campina Boutique LTDA', '33444555000181', ['Moda'], 'Qualificado'),
    ('Lar Doce Lar Móveis LTDA', '44555666000181', ['Casa'], 'Confiável'),
    ('Farmácia Saúde Total LTDA', '55666777000181', ['Saúde'], 'Excelência'),
    ('Padaria Pão Quente LTDA', '66777888000181', ['Alimentação'], 'Qualificado'),
    ('Info Casa Eletrônicos LTDA', '77888999000181', ['Tecnologias', 'Casa'], 'Confiável'),
    ('Clínica Bem Viver LTDA', '88999000000198', ['Saúde'], None),
]

for razao, cnpj, nomes_areas, selo in empresas:
    empresa, _ = Empresa.objects.get_or_create(
        cnpj=cnpj,
        defaults=dict(
            razao_social=razao,
            endereco='Rua Exemplo, 100',
            bairro='Centro',
            cidade='Campina Grande',
            telefone='83999990000',
            email=f'contato@{cnpj}.example.com',
            nivel_selo_atual=selos[selo] if selo else None,
        ),
    )
    empresa.areas.set([areas[a] for a in nomes_areas])

# --- cenários da PB-11 ---
# uma suspensa (some da busca pública)
padaria = Empresa.objects.get(cnpj='66777888000181')
if padaria.status == 'ativo':
    services.alterar_status(padaria, 'suspenso', 'Documentação pendente', gestor)

# uma com revalidação vencida (aparece em revalidacoes-vencidas/)
Empresa.objects.filter(cnpj='77888999000181').update(
    data_proxima_revalidacao=timezone.localdate() - timedelta(days=5)
)

print('Pronto!')
print(f'  {Empresa.objects.count()} empresas, {AreaAtuacao.objects.count()} áreas, {NivelSelo.objects.count()} selos')
print('  usuários: gestor / gestor123  |  analista / analista123')
