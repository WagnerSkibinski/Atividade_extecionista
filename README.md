# Sistema de Validacao de Doacoes - Hemepar Curitiba

Aplicacao web em Django para apoiar o controle de doadores, registro de doacoes e concessao de beneficios por empresas parceiras.

## Tecnologias

- Python 3.12
- Django 6
- SQLite (desenvolvimento)
- HTML e CSS

## Arquitetura MVT

- **Models**: entidades de dominio em `core/models.py`
- **Views**: regras de negocio e renderizacao em `core/views.py`
- **Templates**: paginas HTML em `templates/`

## Entidades principais

- `Doador`: dados do doador vinculado ao usuario
- `Doacao`: registro da doacao e status (pendente, validada, rejeitada)
- `EmpresaParceira`: empresas que oferecem beneficios
- `Beneficio`: regra de beneficio com minimo de doacoes validadas
- `ResgateBeneficio`: historico de beneficios concedidos

## Regras de negocio implementadas

1. Profissionais (usuarios `is_staff`) podem validar doacoes.
2. Beneficios so podem ser concedidos quando o doador atinge o minimo de doacoes validadas.
3. Concessao gera historico auditavel (`ResgateBeneficio`) com usuario responsavel.

## Como executar

1. Ativar ambiente virtual:
   - PowerShell: `./venv/Scripts/Activate.ps1`
2. Instalar dependencias:
   - `pip install -r requirements.txt`
3. Aplicar migracoes:
   - `python manage.py migrate`
4. Criar administrador:
   - `python manage.py createsuperuser`
5. Rodar servidor:
   - `python manage.py runserver`

## Acessos

- Admin: `/admin/`
- Login: `/accounts/login/`
- Dashboard: `/`

## Seguranca e boas praticas (proximos passos)

- Mover `SECRET_KEY` para variavel de ambiente
- Configurar `DEBUG=False` e `ALLOWED_HOSTS` em producao
- Adicionar HTTPS, logs e trilha de auditoria detalhada
- Criar testes para views e permissoes
