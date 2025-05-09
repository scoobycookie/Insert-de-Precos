import cx_Oracle
from dotenv import load_dotenv
import os

load_dotenv('conex.env')

def testar_conexao():
    try:
        dsn = cx_Oracle.makedsn(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            service_name=os.getenv("DB_SERVICE_NAME")  # ← Sem .paas.oracle.com
        )
        
        conn = cx_Oracle.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dsn=dsn
        )
        print("✅ Conexão bem-sucedida!")
        conn.close()
        return True
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"❌ Falha na conexão (Código {error.code}): {error.message}")
        print("💡 Verifique:")
        print("- Service Name exato (sem domínios)")
        print("- Se o IP/porta estão corretos")
        print("- Se o firewall permite conexões na porta 1521")
        return False

if __name__ == "__main__":
    print("=== Teste de Conexão Oracle ===")
    print(f"Tentando conectar em: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_SERVICE_NAME')}")
    testar_conexao()