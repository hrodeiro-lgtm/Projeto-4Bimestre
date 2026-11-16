# NEXO — Cadastro de investimentos

Projeto final de Laboratório de Programação 1. Aplicação web MPA para cadastrar, acompanhar e organizar investimentos, feita com Flask, Jinja2 e SQLite3.

## Como executar

Na pasta que contém o arquivo `run.py`:

```bash
python -m pip install -r requirements.txt
python iniciar_bd.py
python run.py
```

Abra http://127.0.0.1:5055. Para testar, use o usuário `demo` e a senha `NexoDemo2026!`, ou crie uma conta pela tela de cadastro. O banco local é gerado em `data/nexo.sqlite3`. Rodar o script novamente preserva os dados já gravados.

## Funcionalidades

- Usuários: cadastro com hash de senha, login, logout e opção de lembrar o usuário por cookie durante 30 dias.
- Investimentos: cadastro, listagem, edição e exclusão, com cálculo do valor total.
- Categorias: cadastro, listagem e exclusão. Elas servem como sugestões no formulário de investimentos. Cada investimento guarda o texto da categoria.
- Validação no servidor, mensagens temporárias, página 404 personalizada e logs básicos.

## Estrutura MVC

- `iniciar_bd.py`: chama os modelos para criar as tabelas e o usuário de teste.
- `run.py`: inicia o Flask e verifica a inicialização do banco.
- `app/db.py`: abre e fecha o SQLite com `with`, ativa chaves estrangeiras e confirma ou desfaz transações.
- `app/models/`: classes de domínio e SQL parametrizado. As operações nas entidades filtram pelo usuário da sessão.
- `app/controllers/`: Blueprints com rotas e validações.
- `app/views/`: páginas Jinja2 que herdam de `base.html`, com um layout compartilhado para o painel.
- `app/utils/auth_middleware.py`: valida a sessão no banco, disponibiliza o usuário em `g.usuario` e redireciona acessos anônimos.
