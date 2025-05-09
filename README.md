# Projeto de Inserção de Preços

Este projeto é uma aplicação Flask em Python que permite inserir desconto nos preços no banco de dados Oracle de forma prática, a partir de uma interface web simples.

## Funcionalidades

- Upload de dados via textarea
- Suporte a múltiplos formatos: CSV, tabulado, pipe ou espaço
- Validação de colunas obrigatórias
- Tratamento de erros por linha
- Inserção automática no banco com incremento do código de desconto

## Formato esperado dos dados

Com cabeçalho ou não, os dados devem conter **as seguintes colunas**:

```
CODPRODPRINC | NUMREGIAO | PERCDESC | DTINICIO | DTFIM
```

Datas devem estar no formato: `DD/MON/YYYY` (exemplo: `01/JAN/2025`).

## Como rodar localmente

1. Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/seu-repo.git
    cd seu-repo
    ```

2. Crie um ambiente virtual e ative:
    ```bash
    python -m venv venv
    source venv/bin/activate  # no Windows: venv\Scripts\activate
    ```

3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4. Copie o arquivo `.env.example` para `.env` e preencha com suas credenciais Oracle:
    ```bash
    cp .env.example conex.env
    ```

5. Execute a aplicação:
    ```bash
    python app.py
    ```

A aplicação estará acessível em `http://localhost:5000`.

## Estrutura de Arquivos

- `app.py` – aplicação principal com Flask
- `teste_conexao.py` – script auxiliar para validar a conexão Oracle
- `conex.env` – arquivo de variáveis de ambiente (não subir para repositório)
- `templates/index.html` – interface web (adicione ou edite conforme necessário)

## ⚠️ Importante

O repositório está público então é de sua livre espontânea vontade utiliza-lo. No entanto, por favor, lembre-se de não expor suas credencias de banco no arquivo conex.env, mesmo que seja em um repositório privado.

- Nunca suba o arquivo `conex.env` com credenciais reais.
- Adicione o seguinte ao `.gitignore`:
    ```
    conex.env
    *.env
    __pycache__/
    *.pyc
    ```

## Autores

Kelvin - Desenvolvedor Python | BI | Dados | Web  
Williames - DBA | BI | Dados
Lucas - Desenvolvedor Web

Feito com 💻, Red Bull e coragem.
