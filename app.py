from flask import Flask, request, render_template, session, redirect, url_for
import cx_Oracle
import pandas as pd
from io import StringIO
import re
import os
from dotenv import load_dotenv

# Configuração inicial
load_dotenv('conex.env')
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Chave secreta para sessões

# Constantes
REQUIRED_COLS = ['CODPRODPRINC', 'NUMREGIAO', 'PERCDESC', 'DTINICIO', 'DTFIM']
DATE_FORMAT = 'DD/MON/YYYY'

def get_db_connection():
    """Estabelece conexão com o banco Oracle"""
    try:
        dsn = cx_Oracle.makedsn(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            service_name=os.getenv("DB_SERVICE_NAME")
        )
        return cx_Oracle.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dsn=dsn
        )
    except cx_Oracle.DatabaseError as e:
        raise Exception(f"Falha na conexão com o banco: {str(e)}")

def parse_input_data(data):
    """Analisa dados com ou sem cabeçalho, separados por tab, vírgula, pipe ou espaço"""
    try:
        lines = [line.strip() for line in data.split('\n') if line.strip()]
        if not lines:
            return None, "Nenhum dado fornecido"

        # Verifica se tem cabeçalho
        first_line = lines[0].lower()
        has_header = all(col.lower() in first_line for col in REQUIRED_COLS)

        # Junta as linhas pra processar como CSV
        content = '\n'.join(lines)

        # Testa diferentes separadores
        possible_separators = [',', '|', '\t', r'\s+']
        for sep in possible_separators:
            try:
                if sep == r'\s+':
                    df = pd.read_csv(StringIO(content), sep=sep, engine='python')
                else:
                    df = pd.read_csv(StringIO(content), sep=sep)
                
                if has_header:
                    if all(col in df.columns for col in REQUIRED_COLS):
                        return df, None
                else:
                    if len(df.columns) == len(REQUIRED_COLS):
                        df.columns = REQUIRED_COLS
                        return df, None
            except Exception:
                continue  # tenta o próximo separador

        return None, "Formato dos dados inválido ou colunas obrigatórias ausentes."
    
    except Exception as e:
        return None, f"Erro ao processar dados: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    """Rota principal para inserção de descontos"""
    if request.method == 'POST':
        try:
            # Limpa mensagens anteriores
            session.clear()
            
            # Validação básica
            if 'dados' not in request.form or not request.form['dados'].strip():
                raise Exception("Nenhum dado fornecido")
            
            # Processa os dados
            dados_df, error = parse_input_data(request.form['dados'])
            if error:
                raise Exception(error)
            
            # Valida colunas obrigatórias
            missing_cols = [col for col in REQUIRED_COLS if col not in dados_df.columns]
            if missing_cols:
                raise Exception(f"Colunas obrigatórias ausentes: {', '.join(missing_cols)}")
            
            # Conexão e inserção no banco
            connection = get_db_connection()
            try:
                cursor = connection.cursor()
                
                # Obtém o próximo código de desconto
                cursor.execute("SELECT NVL(MAX(CODDESCONTO),0)+1 FROM PCDESCONTO")
                next_cod = cursor.fetchone()[0]
                
                query = f"""
                INSERT INTO PCDESCONTO (
                    CODDESCONTO, CODPRODPRINC, NUMREGIAO, PERCDESC,
                    DTINICIO, DTFIM, BASECREDDEBRCA, ORIGEMPED,
                    APLICADESCONTO, CREDITASOBREPOLITICA, TIPO,
                    ALTERAPTABELA, CODFILIAL, TIPOCONTACORRENTE, TIPOENTREGA
                ) VALUES (
                    :coddesconto, :codprod, :regiao, :desconto,
                    TO_DATE(:dt_inicio, '{DATE_FORMAT}'), TO_DATE(:dt_fim, '{DATE_FORMAT}'),
                    'S', 'F', 'N', 'N', 'C', 'N', '4', 'R', 'T'
                )
                """
                
                success_count = 0
                error_messages = []
                
                for idx, row in dados_df.iterrows():
                    try:
                        regiao = None if pd.isna(row['NUMREGIAO']) or str(row['NUMREGIAO']).lower() in ('null', 'none', '') else int(row['NUMREGIAO'])
                        
                        params = {
                            "coddesconto": next_cod + success_count,
                            "codprod": int(row['CODPRODPRINC']),
                            "regiao": regiao,
                            "desconto": float(str(row['PERCDESC']).replace(",", ".")),
                            "dt_inicio": row['DTINICIO'].strip(),
                            "dt_fim": row['DTFIM'].strip()
                        }
                        
                        cursor.execute(query, params)
                        success_count += 1
                        
                    except Exception as e:
                        error_msg = f"Linha {idx+1}: {str(e)}"
                        error_messages.append(error_msg)
                        continue  # Continua para a próxima linha
                
                connection.commit()
                
                if error_messages:
                    session['warning'] = f"{success_count} registro(s) inserido(s), {len(error_messages)} com erro. Detalhes: {' | '.join(error_messages)}"
                else:
                    session['success'] = f"{success_count} registro(s) inserido(s) com sucesso!"
                
                session['form_data'] = ''  # Limpa o formulário após sucesso
            
            except Exception as e:
                connection.rollback()
                raise e
            finally:
                if 'connection' in locals():
                    connection.close()
            
        except Exception as e:
            session['error'] = str(e)
            session['form_data'] = request.form['dados']  # Mantém os dados para correção
        return redirect(url_for('index'))
    
    # GET request - mostra template com mensagens
    return render_template('index.html',
                         error=session.get('error'),
                         success=session.get('success'),
                         warning=session.get('warning'),
                         form_data=session.get('form_data', ''),
                         required_cols=REQUIRED_COLS,
                         date_format=DATE_FORMAT)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


    #Aos jovens que aqui chegaram deixarei Atena aos seus cuidados kkkkkkk, vlw gnt!!!
    #Feito, por Kelvin