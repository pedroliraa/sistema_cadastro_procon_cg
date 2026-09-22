# Sistema de Cadastro PROCON - Backend

Backend do sistema de cadastro, desenvolvido em Django + Django REST Framework.

## Stack

- Python 3
- Django
- Django REST Framework
- python-decouple (variáveis de ambiente)
- django-cors-headers (CORS para o frontend Angular)

## Requisitos

- Python 3.10+ instalado
- Git

## Como iniciar o projeto (primeira vez)

1. **Clonar o repositório**

   ```bash
   git clone https://github.com/pedroliraa/sistema_cadastro_procon_cg.git
   cd sistema_cadastro_procon_cg
   ```

2. **Trocar para a branch develop**

   ```bash
   git checkout develop
   ```

   > Todo o trabalho novo deve ser feito em branches `feature/*` criadas a partir da `develop`, nunca direto na `main`.

3. **Criar o ambiente virtual**

   ```bash
   python -m venv venv
   ```

4. **Ativar o ambiente virtual**
   - Windows (PowerShell):
     ```powershell
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

5. **Instalar as dependências**

   ```bash
   pip install -r requirements.txt
   ```

6. **Criar o arquivo `.env`**

   Crie um arquivo `.env` na raiz do projeto (esse arquivo NUNCA deve ser commitado) com o seguinte conteúdo, ajustando para os seus dados locais:

   ```env
   SECRET_KEY=troque-por-uma-chave-secreta
   DEBUG=True
   DB_NAME=procon_cg
   DB_USER=postgres
   DB_PASSWORD=sua_senha
   DB_HOST=localhost
   DB_PORT=5432
   ```

7. **Rodar o servidor**

   ```bash
   python manage.py runserver
   ```

   O backend estará disponível em `http://127.0.0.1:8000/`.

## Fluxo de trabalho (GitFlow)

- `main` → código estável/em produção.
- `develop` → branch de integração, onde as features se juntam.
- `feature/nome-da-funcionalidade` → criada a partir da `develop` para cada nova funcionalidade.

Para começar uma nova funcionalidade:

```bash
git checkout develop
git pull
git checkout -b feature/nome-da-funcionalidade
```

Ao terminar, abra um Pull Request de `feature/nome-da-funcionalidade` para `develop` (nunca direto para `main`).

## Dependências (requirements.txt)

- `django`
- `djangorestframework`
- `psycopg2-binary`
- `python-decouple`
- `django-cors-headers`

Se precisar atualizar o arquivo após instalar uma nova lib:

```bash
pip freeze > requirements.txt
```

## Observações

- Nunca versionar: `.env`, `venv/`, `__pycache__/`, `*.pyc`, `db.sqlite3` (já devem estar no `.gitignore`).
- O CORS já vem configurado via `django-cors-headers` para permitir requisições do frontend Angular.

# Sistema de Cadastro PROCON - Frontend

Frontend do sistema de cadastro, desenvolvido em Angular.

## Stack

- Angular (standalone, com SSR/SSG habilitado)
- Tailwind CSS
- TypeScript

## Requisitos

- Node.js (LTS) instalado
- Angular CLI instalado globalmente (`npm install -g @angular/cli`)
- Backend rodando (veja o README da pasta `back/` na raiz do repo)

## Como iniciar o projeto (primeira vez)

1. **Clonar o repositório** (se ainda não tiver feito)

   ```bash
   git clone https://github.com/pedroliraa/sistema_cadastro_procon_cg.git
   cd sistema_cadastro_procon_cg
   ```

2. **Trocar para a branch develop**

   ```bash
   git checkout develop
   ```

   > Todo o trabalho novo deve ser feito em branches `feature/*` criadas a partir da `develop`, nunca direto na `main`.

3. **Entrar na pasta do frontend**

   ```bash
   cd front
   ```

4. **Instalar as dependências**

   ```bash
   npm install --legacy-peer-deps
   ```

   > Use `--legacy-peer-deps` porque algumas versões do npm têm um bug conhecido na resolução de peer dependencies que trava a instalação sem essa flag.

5. **Rodar o projeto**

   ```bash
   ng serve
   ```

   O frontend estará disponível em `http://localhost:4200/`.

## Fluxo de trabalho (GitFlow)

- `main` → código estável/em produção.
- `develop` → branch de integração, onde as features se juntam.
- `feature/nome-da-funcionalidade` → criada a partir da `develop` para cada nova funcionalidade.

Para começar uma nova funcionalidade:

```bash
git checkout develop
git pull
git checkout -b feature/nome-da-funcionalidade
```

Ao terminar, abra um Pull Request de `feature/nome-da-funcionalidade` para `develop` (nunca direto para `main`).

## Módulos previstos

- `consulta-publica`
- `admin`

Para gerar um novo módulo:

```bash
ng generate module nome-do-modulo
```

## Build de produção

```bash
ng build
```

Os arquivos de build vão para a pasta `dist/`.

## Observações

- Nunca versionar: `node_modules/`, `.env`, `dist/`, `.angular/` (já devem estar no `.gitignore`).
- O CORS já está habilitado no backend (via `django-cors-headers`) para aceitar requisições vindas do `http://localhost:4200`.
