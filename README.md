# Sistema de Cadastro PROCON-CG (ProSelo)

Sistema de cadastro de empresas e atribuição de selos de qualidade, com consulta pública e área restrita para a equipe do PROCON-CG / UNIFACISA.

- **back/**: API em Django + Django REST Framework
- **front/**: aplicação em Angular

## Stack

**Back-end**
- Python 3.12+
- Django 6 e Django REST Framework
- PostgreSQL (psycopg2)
- python-decouple (variáveis de ambiente)
- django-cors-headers (CORS para o front)
- drf-spectacular (documentação da API)
- Pillow (upload de fotos das empresas)

**Front-end**
- Angular 21 (standalone components, signals, SSR habilitado)
- Tailwind CSS 4
- TypeScript
- Vitest (testes)

## Requisitos

- Git
- Python 3.12 ou superior
- PostgreSQL
- Node.js 20.19+ (ou 22.12+) e npm
- Angular CLI: `npm install -g @angular/cli`

## Como iniciar o projeto (primeira vez)

1. **Clonar o repositório e trocar para a develop**

   ```bash
   git clone https://github.com/pedroliraa/sistema_cadastro_procon_cg.git
   cd sistema_cadastro_procon_cg
   git checkout develop
   ```

   > Todo trabalho novo é feito em branches `feature/*` criadas a partir da `develop`, nunca direto na `main`.

### Back-end

2. **Criar e ativar o ambiente virtual**

   ```bash
   cd back
   python -m venv venv
   ```

   - Windows (PowerShell): `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. **Instalar as dependências**

   ```bash
   pip install -r requirements.txt
   ```

4. **Criar o banco no PostgreSQL** (ex.: `procon_cg`)

5. **Criar o arquivo `.env`** em `back/core/` (nunca commitar):

   ```env
   SECRET_KEY=troque-por-uma-chave-secreta
   DEBUG=True
   DB_NAME=procon_cg
   DB_USER=postgres
   DB_PASSWORD=sua_senha
   DB_HOST=localhost
   DB_PORT=5432
   ```

6. **Aplicar as migrations e rodar o servidor**

   ```bash
   cd core
   python manage.py migrate
   python manage.py runserver
   ```

   A API fica em `http://127.0.0.1:8000/api/`.
   As migrations já criam os 4 níveis de selo (Qualificado, Confiável, Excelência e Referência).

7. **(Opcional) Dados de exemplo para desenvolvimento**

   ```bash
   python seed_dev.py
   ```

### Front-end

8. **Instalar as dependências e rodar**

   ```bash
   cd front
   npm install --legacy-peer-deps
   npx ng serve
   ```

   O front fica em `http://localhost:4200/`.

   > `--legacy-peer-deps` evita um bug conhecido de resolução de peer dependencies em algumas versões do npm.

   > O endereço da API está em `front/src/app/core/api.ts` (`API_URL`). Para o deploy, basta trocar ali.

## Funcionalidades

**Consulta pública** (sem login)
- Início com busca e empresas em destaque
- Explorar: busca por nome, filtro por categoria e filtro por selo
- Página de Selos, com atalho para as empresas de cada selo

**Área restrita** (login de Analista ou Gestor)
- Lista de empresas com CNPJ mascarado, status, selo e próxima revalidação
- Cadastro e edição de empresas, com foto, áreas de atuação e selo
- Alteração manual de selo, com histórico (quem, quando, selo anterior e motivo)
- Alteração de status (ativo, suspenso, removido) com histórico; remoção apenas pelo Gestor
- Revalidação periódica e lista de revalidações vencidas

## Principais endpoints

| Método | Rota | Uso |
|---|---|---|
| GET | `/api/publico/empresas/?nome=&area=&selo=` | Consulta pública (só empresas ativas) |
| POST | `/api/auth/login/` | Login |
| GET | `/api/auth/me/` | Dados do usuário logado |
| GET/POST | `/api/empresas/` | Listar e cadastrar |
| GET/PATCH | `/api/empresas/<id>/` | Detalhe e edição |
| POST | `/api/empresas/<id>/alterar-status/` | Alterar status |
| POST | `/api/empresas/<id>/alterar-selo/` | Alterar selo |
| POST | `/api/empresas/<id>/revalidar/` | Registrar revalidação |
| GET | `/api/empresas/<id>/historico-status/` | Histórico de status |
| GET | `/api/empresas/<id>/historico-selo/` | Histórico de selos |
| GET | `/api/empresas/revalidacoes-vencidas/` | Revalidações vencidas |
| GET | `/api/areas/` e `/api/niveis-selo/` | Áreas de atuação e níveis de selo |

## Estrutura

```
back/core/
  core/        configurações (settings, urls)
  empresas/    empresas, selos, status e revalidação
  usuarios/    usuários, perfis e permissões
front/src/app/
  core/        serviços, máscaras, selos e guard de autenticação
  pages/       inicio, consulta-publica, selos, login e telas admin-*
```

## Fluxo de trabalho (GitFlow)

- `main`: código estável / produção
- `develop`: integração das features
- `feature/nome-da-funcionalidade`: criada a partir da `develop`

```bash
git switch develop
git pull
git switch -c feature/nome-da-funcionalidade
```

Ao terminar, abra um Pull Request de `feature/...` para `develop` (nunca direto para `main`).

## Comandos úteis

```bash
# back (dentro de back/core)
python manage.py makemigrations
python manage.py migrate
python manage.py check

# front (dentro de front)
npx ng build      # build de produção, saída em dist/
npx ng test       # testes
```

Se instalar uma nova lib no back, atualize o `requirements.txt`:

```bash
pip freeze > requirements.txt
```

## Observações

- Nunca versionar: `.env`, `venv/`, `__pycache__/`, `node_modules/`, `.angular/`, `dist/` e a pasta `media/` (fotos enviadas).
- O CORS está configurado no back para aceitar o front em `http://localhost:4200`.
- As fotos das empresas são salvas em `media/empresas/` no back, então cada ambiente tem as suas.
