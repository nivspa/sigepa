# SIGEPA - Sistema Integrado de Gestão de Casos de Escalpelamento

Sistema web desenvolvido em Django seguindo as melhores práticas arquiteturais para aplicações escaláveis e manuteníveis.

## Estrutura do Projeto

O projeto segue uma arquitetura modular com separação clara de responsabilidades:

```
sigepa/
├── .env                    # Variáveis de ambiente (não versionado)
├── .gitignore             # Arquivos ignorados pelo Git
├── manage.py              # Script de gerenciamento do Django
├── requirements.txt       # Dependências do projeto
├── README.md             # Este arquivo
├── apps/                 # Aplicações Django modulares
│   ├── __init__.py
│   └── usuarios/         # App de gerenciamento de usuários
├── config/               # Configurações do projeto
│   ├── __init__.py
│   ├── settings/         # Configurações divididas por ambiente
│   │   ├── __init__.py
│   │   ├── base.py       # Configurações comuns
│   │   ├── dev.py        # Configurações de desenvolvimento
│   │   └── prod.py       # Configurações de produção
│   ├── urls.py           # URLs principais
│   ├── wsgi.py           # WSGI application
│   └── asgi.py           # ASGI application
├── static/               # Arquivos estáticos
├── media/                # Arquivos de mídia
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   └── usuarios/         # Templates da app usuarios
└── logs/                 # Arquivos de log
```

## Configuração do Ambiente

### 1. Instalação das Dependências

```bash
pip install -r requirements.txt
```

### 2. Configuração do Banco de Dados

O projeto está configurado para usar MySQL. Certifique-se de que o MySQL está rodando e crie o banco de dados:

```sql
CREATE DATABASE sigepa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Configuração das Variáveis de Ambiente

Copie o arquivo `.env` e configure as variáveis necessárias:

```bash
# Configurações de desenvolvimento
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui

# Configurações do banco de dados MySQL
DB_NAME=sigepa_db
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306
```

### 4. Execução das Migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Criação de Superusuário

```bash
python manage.py createsuperuser
```

### 6. Execução do Servidor de Desenvolvimento

```bash
python manage.py runserver
```

O sistema estará disponível em `http://localhost:8000`

## Funcionalidades Implementadas

### Sistema de Usuários

- **Modelo de usuário personalizado** estendendo `AbstractUser`
- **Registro de novos usuários** com campos adicionais
- **Sistema de autenticação** completo
- **Perfil do usuário** com informações detalhadas
- **Interface administrativa** personalizada

### Arquitetura

- **Configurações divididas** por ambiente (dev/prod)
- **Gerenciamento seguro de segredos** com django-environ
- **Estrutura modular** com apps organizadas
- **Templates responsivos** com Bootstrap 5
- **Sistema de logging** configurado

## Tecnologias Utilizadas

- **Django 5.2.6** - Framework web
- **MySQL** - Banco de dados
- **Bootstrap 5** - Framework CSS
- **django-environ** - Gerenciamento de variáveis de ambiente
- **mysqlclient** - Driver MySQL para Python

## Próximos Passos

1. Implementar outras aplicações modulares conforme necessário
2. Adicionar testes automatizados
3. Configurar CI/CD
4. Implementar cache com Redis
5. Adicionar documentação da API (se necessário)

## Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

salsifufu