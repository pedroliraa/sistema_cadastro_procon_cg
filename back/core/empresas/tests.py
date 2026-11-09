from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Empresa, AreaAtuacao, NivelSelo
from .validators import validar_cnpj
from django.db import IntegrityError
from django.test import TestCase


class ValidarCnpjTests(SimpleTestCase):
    def test_aceita_cnpj_numerico_valido(self):
        validar_cnpj('11222333000181')

    def test_aceita_cnpj_alfanumerico_valido(self):
        validar_cnpj('12ABC34501DE35')  # exemplo oficial do Serpro

    def test_rejeita_digito_verificador_errado(self):
        with self.assertRaises(ValidationError):
            validar_cnpj('11222333000182')

    def test_rejeita_pontuacao(self):
        with self.assertRaises(ValidationError):
            validar_cnpj('11.222.333/0001-81')

    def test_rejeita_todos_os_caracteres_iguais(self):
        with self.assertRaises(ValidationError):
            validar_cnpj('00000000000000')


class EmpresaAPITests(APITestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='admin-teste', password='senha-de-teste'
        )
        # PB-06: a API exige perfil interno; Gestor porque o teste de
        # remoção (DELETE) só é permitido a ele.
        usuario.groups.add(Group.objects.get(name='Gestor'))
        self.client.force_authenticate(user=usuario)
        self.url_lista = reverse('empresa-list')
        self.area = AreaAtuacao.objects.create(nome='Alimentos')
        self.dados = {
            'razao_social': 'Mercadinho Boa Compra LTDA',
            'cnpj': '11222333000181',
            'endereco': 'Rua das Flores, 123',
            'bairro': 'Centro',
            'cidade': 'Campina Grande',
            'telefone': '83999998888',
            'email': 'contato@boacompra.example.com',
            'areas': [self.area.pk],
        }

    def criar_empresa(self):
        campos = {k: v for k, v in self.dados.items() if k != 'areas'}
        empresa = Empresa.objects.create(**campos)
        empresa.areas.set([self.area])
        return empresa

    def test_cria_empresa(self):
        resposta = self.client.post(self.url_lista, self.dados, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        empresa = Empresa.objects.get()
        self.assertEqual(empresa.cnpj, self.dados['cnpj'])
        self.assertEqual(list(empresa.areas.all()), [self.area])
        self.assertEqual(empresa.status, 'ativo')

    def test_nao_cria_com_cnpj_invalido(self):
        self.dados['cnpj'] = '11222333000182'
        resposta = self.client.post(self.url_lista, self.dados, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cnpj', resposta.data)
        self.assertEqual(Empresa.objects.count(), 0)

    def test_nao_cria_com_cnpj_duplicado(self):
        self.criar_empresa()
        resposta = self.client.post(self.url_lista, self.dados, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cnpj', resposta.data)

    def test_nao_cria_sem_campo_obrigatorio(self):
        del self.dados['razao_social']
        resposta = self.client.post(self.url_lista, self.dados, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('razao_social', resposta.data)

    def test_nao_cria_sem_area_de_atuacao(self):
        self.dados['areas'] = []
        resposta = self.client.post(self.url_lista, self.dados, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('areas', resposta.data)

    def test_ignora_status_enviado_na_criacao(self):
        self.dados['status'] = 'removido'
        resposta = self.client.post(self.url_lista, self.dados, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Empresa.objects.get().status, 'ativo')

    def test_lista_empresas(self):
        self.criar_empresa()
        resposta = self.client.get(self.url_lista)
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resposta.data['results']), 1)

    def test_detalha_empresa(self):
        empresa = self.criar_empresa()
        resposta = self.client.get(reverse('empresa-detail', args=[empresa.pk]))
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['razao_social'], self.dados['razao_social'])

    def test_atualiza_parcialmente(self):
        empresa = self.criar_empresa()
        resposta = self.client.patch(
            reverse('empresa-detail', args=[empresa.pk]),
            {'telefone': '8333334444'},
            format='json',
        )
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        empresa.refresh_from_db()
        self.assertEqual(empresa.telefone, '8333334444')

    def test_remove_empresa(self):
        empresa = self.criar_empresa()
        resposta = self.client.delete(reverse('empresa-detail', args=[empresa.pk]))
        self.assertEqual(resposta.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Empresa.objects.count(), 0)

    def test_exige_autenticacao(self):
        self.client.force_authenticate(user=None)
        resposta = self.client.get(self.url_lista)
        self.assertIn(
            resposta.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
class GestaoAreasAtuacaoTests(TestCase):

    def test_cadastra_area_de_atuacao(self):
        area = AreaAtuacao.objects.create(nome="Comércio")

        self.assertEqual(area.nome, "Comércio")
        self.assertEqual(str(area), "Comércio")

    def test_nao_permite_area_com_nome_duplicado(self):
        AreaAtuacao.objects.create(nome="Alimentação")

        with self.assertRaises(IntegrityError):
            AreaAtuacao.objects.create(nome="Alimentação")

    def test_edita_area_de_atuacao(self):
        area = AreaAtuacao.objects.create(nome="Comércio")

        area.nome = "Comércio varejista"
        area.save()
        area.refresh_from_db()

        self.assertEqual(area.nome, "Comércio varejista")

    def test_empresa_pode_ter_multiplas_areas(self):
        area_comercio = AreaAtuacao.objects.create(nome="Comércio")
        area_alimentacao = AreaAtuacao.objects.create(nome="Alimentação")

        empresa = Empresa.objects.create(
            razao_social="Mercadinho Boa Compra LTDA",
            cnpj="11222333000181",
            endereco="Rua das Flores, 123",
            bairro="Centro",
            cidade="Campina Grande",
            telefone="83999998888",
            email="contato@boacompra.example.com",
        )

        empresa.areas.set([area_comercio, area_alimentacao])

        self.assertEqual(empresa.areas.count(), 2)
        self.assertIn(area_comercio, empresa.areas.all())
        self.assertIn(area_alimentacao, empresa.areas.all())

    def test_exclui_area_de_atuacao(self):
        area = AreaAtuacao.objects.create(nome="Tecnologia")

        area.delete()

        self.assertFalse(
            AreaAtuacao.objects.filter(nome="Tecnologia").exists()
        )

class EmpresaBuscaPublicaTests(APITestCase):

    def setUp(self):
        self.url = reverse('empresa-busca-publica')

        self.empresa = Empresa.objects.create(
            razao_social='Mercadinho Boa Compra LTDA',
            cnpj='11222333000181',
            endereco='Rua das Flores, 123',
            bairro='Centro',
            cidade='Campina Grande',
            telefone='83999998888',
            email='contato@boacompra.example.com',
        )

    def test_busca_por_nome_sem_login(self):
        resposta = self.client.get(self.url, {'nome': 'mercadinho'})

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['count'], 1)
        self.assertEqual(
            resposta.data['results'][0]['razao_social'],
            'Mercadinho Boa Compra LTDA'
        )

    def test_busca_sem_nome_retorna_lista_vazia(self):
        resposta = self.client.get(self.url)

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['count'], 0)

    def test_nao_expoe_dados_privados(self):
        resposta = self.client.get(self.url, {'nome': 'mercadinho'})

        empresa = resposta.data['results'][0]

        self.assertIn('razao_social', empresa)
        self.assertNotIn('cnpj', empresa)
        self.assertNotIn('telefone', empresa)
        self.assertNotIn('email', empresa)

    def test_nao_exibe_empresa_removida(self):
        self.empresa.status = 'removido'
        self.empresa.save()

        resposta = self.client.get(self.url, {'nome': 'mercadinho'})

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['count'], 0)
    def test_busca_por_area_sem_login(self):
        area = AreaAtuacao.objects.create(nome='Alimentação')
        self.empresa.areas.add(area)

        resposta = self.client.get(
            self.url,
            {'area': 'alimentação'}
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['count'], 1)
        self.assertEqual(
            resposta.data['results'][0]['razao_social'],
            'Mercadinho Boa Compra LTDA'
        )

    def test_busca_por_empresa_com_multiplas_areas(self):
        tecnologia = AreaAtuacao.objects.create(nome='Tecnologia')
        alimentacao = AreaAtuacao.objects.create(nome='Alimentação')

        self.empresa.areas.add(tecnologia, alimentacao)

        resposta = self.client.get(
            self.url,
            {'area': 'tecnologia'}
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['count'], 1)
        self.assertEqual(
            resposta.data['results'][0]['razao_social'],
            'Mercadinho Boa Compra LTDA'
        )

    def test_busca_por_area_nao_exibe_empresa_removida(self):
        area = AreaAtuacao.objects.create(nome='Alimentação')
        self.empresa.areas.add(area)

        self.empresa.status = 'removido'
        self.empresa.save()

        resposta = self.client.get(
            self.url,
            {'area': 'alimentação'}
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['count'], 0)
    def test_exibe_selo_atual_sem_login(self):
        selo = NivelSelo.objects.create(nome='Ouro')
        self.empresa.nivel_selo_atual = selo
        self.empresa.save()

        resposta = self.client.get(
            self.url,
            {'nome': 'mercadinho'}
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['count'], 1)
        self.assertEqual(resposta.data['results'][0]['selo'], 'Ouro')



# ============================================================
# PB-11: alteração de status, revalidação periódica, histórico
# ============================================================
from datetime import date, timedelta
from io import StringIO

from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from .models import HistoricoStatus, somar_meses
from .signals import status_alterado


def nova_empresa(**extra):
    dados = dict(
        razao_social='Mercadinho Boa Compra LTDA',
        cnpj='11222333000181',
        endereco='Rua das Flores, 123',
        bairro='Centro',
        cidade='Campina Grande',
        telefone='83999998888',
        email='contato@boacompra.example.com',
    )
    dados.update(extra)
    return Empresa.objects.create(**dados)


class SomarMesesTests(SimpleTestCase):
    def test_soma_simples(self):
        self.assertEqual(somar_meses(date(2026, 3, 10), 6), date(2026, 9, 10))

    def test_vira_o_ano(self):
        self.assertEqual(somar_meses(date(2026, 9, 15), 6), date(2027, 3, 15))

    def test_ajusta_fim_de_mes(self):
        self.assertEqual(somar_meses(date(2026, 8, 31), 6), date(2027, 2, 28))


class RevalidacaoModeloTests(TestCase):
    def test_empresa_nova_ja_tem_prazo_de_revalidacao(self):
        empresa = nova_empresa()
        hoje = timezone.localdate()
        self.assertEqual(empresa.data_ultima_validacao, hoje)
        self.assertEqual(empresa.data_proxima_revalidacao, somar_meses(hoje, 6))
        self.assertFalse(empresa.revalidacao_vencida)

    @override_settings(REVALIDACAO_MESES=12)
    def test_periodicidade_configuravel(self):
        empresa = nova_empresa()
        self.assertEqual(
            empresa.data_proxima_revalidacao,
            somar_meses(timezone.localdate(), 12),
        )

    def test_revalidacao_vencida(self):
        empresa = nova_empresa()
        empresa.data_proxima_revalidacao = timezone.localdate() - timedelta(days=1)
        empresa.save()
        self.assertTrue(empresa.revalidacao_vencida)

    def test_removida_nao_conta_como_vencida(self):
        empresa = nova_empresa(status='removido')
        empresa.data_proxima_revalidacao = timezone.localdate() - timedelta(days=1)
        empresa.save()
        self.assertFalse(empresa.revalidacao_vencida)


class AlteracaoStatusAPITests(APITestCase):
    def setUp(self):
        self.gestor = get_user_model().objects.create_user(
            username='gestor-teste', password='senha-de-teste'
        )
        self.gestor.groups.add(Group.objects.get(name='Gestor'))
        self.analista = get_user_model().objects.create_user(
            username='analista-teste', password='senha-de-teste'
        )
        self.analista.groups.add(Group.objects.get(name='Analista'))

        self.client.force_authenticate(user=self.gestor)
        self.empresa = nova_empresa()

    def url(self, nome):
        return reverse(f'empresa-{nome}', args=[self.empresa.pk])

    def alterar(self, novo_status, motivo='Descumprimento de critério'):
        return self.client.post(
            self.url('alterar-status'),
            {'status': novo_status, 'motivo': motivo},
            format='json',
        )

    # --- transições ---

    def test_suspende_empresa_e_grava_historico(self):
        resposta = self.alterar('suspenso')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['status'], 'suspenso')

        historico = HistoricoStatus.objects.get()
        self.assertEqual(historico.tipo, 'alteracao')
        self.assertEqual(historico.status_anterior, 'ativo')
        self.assertEqual(historico.status_novo, 'suspenso')
        self.assertEqual(historico.motivo, 'Descumprimento de critério')
        self.assertEqual(historico.usuario, self.gestor)

    def test_reativa_empresa_suspensa(self):
        self.alterar('suspenso')
        resposta = self.alterar('ativo', 'Pendência resolvida')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['status'], 'ativo')

    def test_gestor_remove_empresa(self):
        resposta = self.alterar('removido')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.empresa.refresh_from_db()
        self.assertEqual(self.empresa.status, 'removido')
        # remoção por descumprimento não apaga o cadastro
        self.assertTrue(Empresa.objects.filter(pk=self.empresa.pk).exists())

    def test_exige_motivo(self):
        resposta = self.alterar('suspenso', motivo='   ')
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.empresa.refresh_from_db()
        self.assertEqual(self.empresa.status, 'ativo')

    def test_rejeita_status_inexistente(self):
        resposta = self.alterar('cancelado')
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejeita_mesmo_status(self):
        resposta = self.alterar('ativo')
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(HistoricoStatus.objects.count(), 0)

    def test_status_continua_bloqueado_no_crud(self):
        resposta = self.client.patch(
            reverse('empresa-detail', args=[self.empresa.pk]),
            {'status': 'suspenso'},
            format='json',
        )
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.empresa.refresh_from_db()
        self.assertEqual(self.empresa.status, 'ativo')

    # --- permissões ---

    def test_analista_pode_suspender(self):
        self.client.force_authenticate(user=self.analista)
        resposta = self.alterar('suspenso')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)

    def test_analista_nao_pode_remover(self):
        self.client.force_authenticate(user=self.analista)
        resposta = self.alterar('removido')
        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)
        self.empresa.refresh_from_db()
        self.assertEqual(self.empresa.status, 'ativo')

    def test_analista_nao_pode_reativar_removida(self):
        self.alterar('removido')
        self.client.force_authenticate(user=self.analista)
        resposta = self.alterar('ativo', 'Tentativa')
        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)

    def test_exige_autenticacao(self):
        self.client.force_authenticate(user=None)
        resposta = self.alterar('suspenso')
        self.assertIn(
            resposta.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    # --- consulta pública ---

    def test_suspensa_some_da_busca_publica(self):
        self.alterar('suspenso')
        self.client.force_authenticate(user=None)
        resposta = self.client.get(reverse('empresa-busca-publica'), {'nome': 'mercadinho'})
        self.assertEqual(resposta.data['count'], 0)

    # --- gancho da PB-12 ---

    def test_dispara_signal_de_status_alterado(self):
        recebidos = []

        def receptor(sender, **kwargs):
            recebidos.append(kwargs)

        status_alterado.connect(receptor)
        self.addCleanup(status_alterado.disconnect, receptor)

        with self.captureOnCommitCallbacks(execute=True):
            self.alterar('suspenso')

        self.assertEqual(len(recebidos), 1)
        self.assertEqual(recebidos[0]['empresa'].pk, self.empresa.pk)
        self.assertEqual(recebidos[0]['status_anterior'], 'ativo')
        self.assertEqual(recebidos[0]['status_novo'], 'suspenso')

    def test_nao_dispara_signal_se_transicao_invalida(self):
        recebidos = []

        def receptor(sender, **kwargs):
            recebidos.append(kwargs)

        status_alterado.connect(receptor)
        self.addCleanup(status_alterado.disconnect, receptor)

        with self.captureOnCommitCallbacks(execute=True):
            self.alterar('ativo')

        self.assertEqual(recebidos, [])

    # --- revalidação ---

    def test_revalida_e_renova_prazo(self):
        ontem = timezone.localdate() - timedelta(days=1)
        Empresa.objects.filter(pk=self.empresa.pk).update(
            data_ultima_validacao=ontem - timedelta(days=200),
            data_proxima_revalidacao=ontem,
        )

        resposta = self.client.post(self.url('revalidar'), {}, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)

        hoje = timezone.localdate()
        self.assertEqual(resposta.data['data_ultima_validacao'], hoje.isoformat())
        self.assertEqual(
            resposta.data['data_proxima_revalidacao'], somar_meses(hoje, 6).isoformat()
        )
        self.assertFalse(resposta.data['revalidacao_vencida'])

        historico = HistoricoStatus.objects.get()
        self.assertEqual(historico.tipo, 'revalidacao')

    def test_revalidar_nao_reativa_suspensa(self):
        self.alterar('suspenso')
        resposta = self.client.post(self.url('revalidar'), {}, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(resposta.data['status'], 'suspenso')

    def test_nao_revalida_removida(self):
        self.alterar('removido')
        resposta = self.client.post(self.url('revalidar'), {}, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lista_revalidacoes_vencidas(self):
        outra = nova_empresa(razao_social='Outra LTDA', cnpj='12ABC34501DE35')
        Empresa.objects.filter(pk=outra.pk).update(
            data_proxima_revalidacao=timezone.localdate() - timedelta(days=3)
        )

        resposta = self.client.get(reverse('empresa-revalidacoes-vencidas'))
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        ids = [e['id'] for e in resposta.data['results']]
        self.assertEqual(ids, [outra.pk])

    # --- histórico ---

    def test_historico_mais_recente_primeiro(self):
        self.alterar('suspenso', 'Primeiro')
        self.alterar('ativo', 'Segundo')

        resposta = self.client.get(self.url('historico-status'))
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        motivos = [h['motivo'] for h in resposta.data['results']]
        self.assertEqual(motivos, ['Segundo', 'Primeiro'])
        self.assertEqual(resposta.data['results'][0]['usuario'], 'gestor-teste')


class VerificarRevalidacoesCommandTests(TestCase):
    def setUp(self):
        self.vencida = nova_empresa()
        Empresa.objects.filter(pk=self.vencida.pk).update(
            data_proxima_revalidacao=timezone.localdate() - timedelta(days=1)
        )
        self.em_dia = nova_empresa(razao_social='Em Dia LTDA', cnpj='12ABC34501DE35')

    def test_so_lista_sem_suspender(self):
        saida = StringIO()
        call_command('verificar_revalidacoes', stdout=saida)
        self.assertIn('Mercadinho Boa Compra LTDA', saida.getvalue())
        self.assertNotIn('Em Dia LTDA', saida.getvalue())
        self.vencida.refresh_from_db()
        self.assertEqual(self.vencida.status, 'ativo')

    def test_suspende_vencidas(self):
        call_command('verificar_revalidacoes', '--suspender', stdout=StringIO())

        self.vencida.refresh_from_db()
        self.em_dia.refresh_from_db()
        self.assertEqual(self.vencida.status, 'suspenso')
        self.assertEqual(self.em_dia.status, 'ativo')

        historico = HistoricoStatus.objects.get(empresa=self.vencida)
        self.assertIn('revalidação vencida', historico.motivo)
        self.assertIsNone(historico.usuario)

    def test_sem_vencidas(self):
        Empresa.objects.filter(pk=self.vencida.pk).update(
            data_proxima_revalidacao=timezone.localdate() + timedelta(days=10)
        )
        saida = StringIO()
        call_command('verificar_revalidacoes', stdout=saida)
        self.assertIn('Nenhuma revalidação vencida', saida.getvalue())
