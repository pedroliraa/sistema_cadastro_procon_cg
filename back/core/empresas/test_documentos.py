import shutil
import tempfile

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import DocumentoComprobatorio, Empresa

PDF = b'%PDF-1.4\nconteudo de teste\n'
MEDIA_TMP = tempfile.mkdtemp()


def arquivo(nome='comprovante.pdf', conteudo=PDF):
    return SimpleUploadedFile(nome, conteudo)


@override_settings(MEDIA_ROOT=MEDIA_TMP)
class DocumentoComprobatorioTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_TMP, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.analista = User.objects.create_user('ana', password='senha12345')
        self.analista.groups.add(Group.objects.get(name='Analista'))
        self.gestor = User.objects.create_user('gil', password='senha12345')
        self.gestor.groups.add(Group.objects.get(name='Gestor'))
        self.sem_perfil = User.objects.create_user('ze', password='senha12345')

        self.empresa = self.criar_empresa('11222333000181')
        self.url = reverse('empresa-documento-list', args=[self.empresa.pk])

    def criar_empresa(self, cnpj):
        return Empresa.objects.create(
            razao_social='Empresa Teste', cnpj=cnpj,
            endereco='Rua A, 1', bairro='Centro', cidade='Campina Grande',
            telefone='83999999999', email='contato@teste.com',
        )

    def enviar(self, **kwargs):
        return self.client.post(self.url, {'arquivo': arquivo(**kwargs)}, format='multipart')

    def criar_documento(self, empresa=None):
        self.client.force_authenticate(self.analista)
        url = reverse('empresa-documento-list', args=[(empresa or self.empresa).pk])
        r = self.client.post(url, {'arquivo': arquivo()}, format='multipart')
        return r.data['id']

    # envio
    def test_analista_envia_pdf(self):
        self.client.force_authenticate(self.analista)
        r = self.enviar()
        self.assertEqual(r.status_code, 201, r.data)
        doc = DocumentoComprobatorio.objects.get()
        self.assertEqual(doc.empresa, self.empresa)
        self.assertEqual(doc.enviado_por, self.analista)
        self.assertEqual(doc.nome_original, 'comprovante.pdf')
        self.assertNotIn('comprovante', doc.arquivo.name)  # nome aleatório

    def test_gestor_envia_png(self):
        self.client.force_authenticate(self.gestor)
        r = self.enviar(nome='foto.png', conteudo=b'\x89PNG\r\n\x1a\nxxxx')
        self.assertEqual(r.status_code, 201, r.data)

    def test_sem_login_nao_envia(self):
        self.assertIn(self.enviar().status_code, (401, 403))

    def test_sem_perfil_nao_envia(self):
        self.client.force_authenticate(self.sem_perfil)
        self.assertEqual(self.enviar().status_code, 403)

    def test_rejeita_extensao_invalida(self):
        self.client.force_authenticate(self.analista)
        r = self.enviar(nome='virus.exe', conteudo=b'MZ....')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(DocumentoComprobatorio.objects.count(), 0)

    def test_rejeita_conteudo_diferente_da_extensao(self):
        self.client.force_authenticate(self.analista)
        r = self.enviar(nome='falso.pdf', conteudo=b'isso nao e um pdf')
        self.assertEqual(r.status_code, 400)

    def test_rejeita_arquivo_acima_de_5mb(self):
        self.client.force_authenticate(self.analista)
        grande = b'%PDF-' + b'0' * (5 * 1024 * 1024 + 1)
        r = self.enviar(conteudo=grande)
        self.assertEqual(r.status_code, 400)

    def test_rejeita_sem_arquivo(self):
        self.client.force_authenticate(self.analista)
        r = self.client.post(self.url, {}, format='multipart')
        self.assertEqual(r.status_code, 400)

    def test_empresa_inexistente_404(self):
        self.client.force_authenticate(self.analista)
        url = reverse('empresa-documento-list', args=[99999])
        r = self.client.post(url, {'arquivo': arquivo()}, format='multipart')
        self.assertEqual(r.status_code, 404)

    # listagem
    def test_lista_apenas_documentos_da_empresa(self):
        outra = self.criar_empresa('11444777000161')
        self.criar_documento()
        self.criar_documento(empresa=outra)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)
        self.assertNotIn('arquivo', r.data['results'][0])

    # download
    def test_download_retorna_o_arquivo(self):
        doc_id = self.criar_documento()
        url = reverse('empresa-documento-download', args=[self.empresa.pk, doc_id])
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(b''.join(r.streaming_content), PDF)
        self.assertIn('attachment', r['Content-Disposition'])

    def test_download_sem_login_bloqueado(self):
        doc_id = self.criar_documento()
        self.client.force_authenticate(None)
        url = reverse('empresa-documento-download', args=[self.empresa.pk, doc_id])
        self.assertIn(self.client.get(url).status_code, (401, 403))

    # exclusão
    def test_analista_nao_exclui(self):
        doc_id = self.criar_documento()
        url = reverse('empresa-documento-detail', args=[self.empresa.pk, doc_id])
        self.assertEqual(self.client.delete(url).status_code, 403)
        self.assertEqual(DocumentoComprobatorio.objects.count(), 1)

    def test_gestor_exclui_e_apaga_o_arquivo(self):
        doc_id = self.criar_documento()
        doc = DocumentoComprobatorio.objects.get(pk=doc_id)
        caminho = doc.arquivo.name
        self.client.force_authenticate(self.gestor)
        url = reverse('empresa-documento-detail', args=[self.empresa.pk, doc_id])
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertFalse(doc.arquivo.storage.exists(caminho))