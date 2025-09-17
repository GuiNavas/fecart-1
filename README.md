# Fecart

Aplicação Flask com SQLite para cálculo de pegada de carbono e quiz.

## Requisitos
- Python 3.11+ (ou compatível)

## Configuração e execução

1. Criar ambiente virtual e instalar dependências:
```bash
py -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
```

2. Inicializar o banco de dados (opcional, o app também cria ao subir):
```bash
.\.venv\Scripts\python init_db.py
```

3. Executar a aplicação:
```bash
.\.venv\Scripts\python app.py
```

4. Acessar no navegador:
- http://localhost:5000/

## Estrutura
- `app.py`: app Flask, modelos e rotas.
- `init_db.py`: inicializa o banco `verdetch.db`.
- `requirements.txt`: dependências do projeto.
- `static/` e `templates/` (se existirem): assets e pages.

## Publicando no GitHub
1. Inicialize o repositório, faça o commit inicial e crie a branch principal:
```bash
git init
git add .
git commit -m "Initial commit: Flask app + SQLite"
```
2. Crie um repositório no GitHub e adicione o remoto:
```bash
git branch -M main
git remote add origin https://github.com/<seu-usuario>/<seu-repo>.git
git push -u origin main
```

## Observações
- O arquivo `verdetch.db` está ignorado no Git por padrão.


