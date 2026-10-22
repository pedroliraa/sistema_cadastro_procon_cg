from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import AreaAtuacao, Empresa
from .validators import validar_cnpj


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
