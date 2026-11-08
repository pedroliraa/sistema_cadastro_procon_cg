from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APITestCase

from empresas.models import AreaAtuacao, Empresa

SENHA = "senha12345"


def criar_usuario(username, perfil=None, **extra):
    user = User.objects.create_user(username, password=SENHA, **extra)
    if perfil:
        user.groups.add(Group.objects.get(name=perfil))
    return user


class BaseTest(APITestCase):
    def setUp(self):
        self.analista = criar_usuario("ana", "Analista")
        self.gestor = criar_usuario("gil", "Gestor")
        self.sem_perfil = criar_usuario("zé")  # logado, mas sem grupo

        self.area = AreaAtuacao.objects.create(nome="Alimentação")
        self.empresa = Empresa.objects.create(
            razao_social="Empresa Teste",
            cnpj="11222333000181",
            endereco="Rua A, 1",
            bairro="Centro",
            cidade="Campina Grande",
            telefone="83999999999",
            email="contato@teste.com",
        )
        self.empresa.areas.add(self.area)

    def login(self, user):
        self.client.force_authenticate(user)


class GruposTest(BaseTest):
    def test_grupos_foram_criados_pela_migration(self):
        nomes = set(Group.objects.values_list("name", flat=True))
        self.assertTrue({"Analista", "Gestor"}.issubset(nomes))


class AutenticacaoTest(BaseTest):
    

    def test_me_sem_login_401(self):
        self.assertIn(self.client.get("/api/auth/me/").status_code, (401, 403))

    def test_me_retorna_perfil_analista(self):
        self.login(self.analista)
        r = self.client.get("/api/auth/me/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["perfil"], "Analista")

    def test_me_retorna_perfil_gestor(self):
        self.login(self.gestor)
        r = self.client.get("/api/auth/me/")
        self.assertEqual(r.data["perfil"], "Gestor")

    def test_me_sem_perfil_403(self):
        self.login(self.sem_perfil)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 403)


class GestaoUsuariosTest(BaseTest):
    url = "/api/usuarios/"

    def novo_usuario(self, perfil="Analista"):
        return {
            "username": "novo",
            "email": "novo@procon.com",
            "password": "senha12345",
            "perfil": perfil,
        }

    def test_sem_login_401(self):
        self.assertIn(self.client.get(self.url).status_code, (401, 403))

    def test_analista_nao_acessa(self):
        self.login(self.analista)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_sem_perfil_nao_acessa(self):
        self.login(self.sem_perfil)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_gestor_lista(self):
        self.login(self.gestor)
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_gestor_cria_analista(self):
        self.login(self.gestor)
        r = self.client.post(self.url, self.novo_usuario("Analista"))
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["perfil"], "Analista")
        self.assertNotIn("password", r.data)
        novo = User.objects.get(username="novo")
        self.assertTrue(novo.check_password("senha12345"))
        self.assertTrue(novo.groups.filter(name="Analista").exists())

    def test_gestor_cria_gestor(self):
        self.login(self.gestor)
        r = self.client.post(self.url, self.novo_usuario("Gestor"))
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["perfil"], "Gestor")

    def test_perfil_invalido_400(self):
        self.login(self.gestor)
        r = self.client.post(self.url, self.novo_usuario("Presidente"))
        self.assertEqual(r.status_code, 400)

    def test_senha_curta_400(self):
        self.login(self.gestor)
        dados = self.novo_usuario()
        dados["password"] = "123"
        self.assertEqual(self.client.post(self.url, dados).status_code, 400)

    def test_gestor_troca_perfil_de_usuario(self):
        self.login(self.gestor)
        r = self.client.patch(f"{self.url}{self.analista.id}/", {"perfil": "Gestor"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["perfil"], "Gestor")
        self.assertEqual(self.analista.groups.count(), 1)

    def test_analista_nao_cria_usuario(self):
        self.login(self.analista)
        r = self.client.post(self.url, self.novo_usuario())
        self.assertEqual(r.status_code, 403)


class PermissoesEmpresaTest(BaseTest):
    """Testa as permissões do EmpresaViewSet sem alterar o app empresas."""

    def dados_empresa(self):
        return {
            "razao_social": "Nova Empresa",
            "cnpj": "11444777000161",
            "endereco": "Rua B, 2",
            "bairro": "Centro",
            "cidade": "Campina Grande",
            "telefone": "83988887777",
            "email": "nova@empresa.com",
            "areas": [self.area.id],
        }

    def test_sem_login_401(self):
       self.assertIn(self.client.get(reverse("empresa-list")).status_code, (401, 403))

    def test_sem_perfil_403(self):
        self.login(self.sem_perfil)
        self.assertEqual(self.client.get(reverse("empresa-list")).status_code, 403)

    def test_analista_lista_e_ve_detalhe(self):
        self.login(self.analista)
        self.assertEqual(self.client.get(reverse("empresa-list")).status_code, 200)
        r = self.client.get(reverse("empresa-detail", args=[self.empresa.id]))
        self.assertEqual(r.status_code, 200)

    def test_analista_cria_empresa(self):
        self.login(self.analista)
        r = self.client.post(reverse("empresa-list"), self.dados_empresa())
        self.assertEqual(r.status_code, 201, r.data)

    def test_analista_edita_empresa(self):
        self.login(self.analista)
        r = self.client.patch(
            reverse("empresa-detail", args=[self.empresa.id]),
            {"bairro": "Catolé"},
        )
        self.assertEqual(r.status_code, 200)

    def test_analista_nao_exclui(self):
        self.login(self.analista)
        r = self.client.delete(reverse("empresa-detail", args=[self.empresa.id]))
        self.assertEqual(r.status_code, 403)
        self.assertTrue(Empresa.objects.filter(id=self.empresa.id).exists())

    def test_gestor_exclui(self):
        self.login(self.gestor)
        r = self.client.delete(reverse("empresa-detail", args=[self.empresa.id]))
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Empresa.objects.filter(id=self.empresa.id).exists())

    def test_gestor_cria_empresa(self):
        self.login(self.gestor)
        r = self.client.post(reverse("empresa-list"), self.dados_empresa())
        self.assertEqual(r.status_code, 201, r.data)
