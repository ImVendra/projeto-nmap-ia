import os
import sys
import time
import subprocess
import requests
import signal
import logging
from api.parser_nmap import parse_nmap_xml

# Define caminho da raiz do projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
SCAN_FILE = os.path.join(BASE_DIR, "data", "exemplos_xml", "scan.xml")
API_URL = "http://127.0.0.1:8000/classificar"

# CONFIGURAÇÃO DE LOG
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "log.txt")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def log(msg):
    print(msg)
    logging.info(msg)


def log_error(msg):
    print("[ERRO] ", msg)
    logging.error(msg)


def treinar_modelo():
    log("[+] Iniciando treinamento...")

    try:
        treino_script = os.path.join(BASE_DIR, "model", "treino_modelo.py")
        subprocess.run(["python", treino_script], check=True)
        log("[✔] Treinamento concluído.")
    except Exception as e:
        log_error(f"Erro ao treinar modelo: {e}")
        exit()


def iniciar_api():
    log("[+] Iniciando API FastAPI...")

    api_script = os.path.join(BASE_DIR, "api", "api.py")

    try:
        process = subprocess.Popen(
            ["uvicorn", "api.api:app"],
            cwd=os.path.join(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    except Exception as e:
        log_error(f"Erro ao iniciar API: {e}")
        exit()

    # Aguarda API subir
    log("[+] Aguardando API iniciar...")
    time.sleep(3)

    # Testa se API está respondendo
    try:
        r = requests.get("http://127.0.0.1:8000/")
        log("[✔] API iniciada com sucesso.")
    except:
        log_error("A API não respondeu — encerrando.")
        process.kill()
        exit()

    return process


def parar_api(process):
    log("\n[+] Encerrando API...")
    try:
        process.send_signal(signal.CTRL_BREAK_EVENT)
        log("[✔] API encerrada.")
    except Exception as e:
        log_error(f"Erro ao encerrar API: {e}")


def run_nmap(target):
    log(f"[+] Executando Nmap em {target}...")
    NMAP_PATH = r"C:\Program Files (x86)\Nmap\nmap.exe"  # caminho do executavel do nmap
    comando = [NMAP_PATH, "-sV", "-oX", SCAN_FILE, target]

    try:
        result = subprocess.run(comando, capture_output=True, text=True)
        # subprocess.run(comando)
        logging.info(result.stdout)  # saida nmap
        log("[+] Scan concluído.")
    except Exception as e:
        log_error(f"Falha ao executar Nmap: {e}")


def normalizar_servico(nome):
    if nome is None:
        return "unknown"

    nome = nome.lower().strip()

    # Correções diretas
    nome = nome.replace("?", "")
    nome = nome.replace("/", "")
    nome = nome.replace(" ", "-")

    # Reduções semânticas
    if "http" in nome:
        return "http"
    if "https" in nome:
        return "https"
    if "msrpc" in nome:
        return "msrpc"
    if "microsoft-ds" in nome:
        return "microsoft-ds"
    if "rpc" in nome:
        return "rpcbind"
    if "sql" in nome or "mssql" in nome:
        return "mssql"
    if "mysql" in nome:
        return "mysql"
    if "ldap" in nome:
        return "ldap"
    if "ftp" in nome:
        return "ftp"
    if "ssh" in nome:
        return "ssh"
    if "smtp" in nome or "smtps" in nome:
        return "smtp"
    if "dns" in nome:
        return "dns"

    return nome


def classificar_resultados():
    log("[+] Lendo XML do Nmap...")
    resultados = parse_nmap_xml(SCAN_FILE)

    log("[+] Classificando riscos com IA...\n")
    for item in resultados:
        if item["estado"] != "open":
            continue

        payload = {
            "porta": item["porta"],
            "servico": normalizar_servico(item["servico"]),
            "protocolo": item["protocolo"],
        }

        try:
            resposta = requests.post(API_URL, json=payload).json()

            # A API retorna {"risco": "..."}
            # risco = resposta.get("risco") or resposta.get("risco_classificado")
            risco = resposta.get("risco_classificado")

            log(f"Porta {item["porta"]} ({item["servico"]}) → Risco: {risco}")

        except Exception as e:
            log_error(f"Erro ao conectar com a API: {e}")


if __name__ == "__main__":
    log("===== INÍCIO DO PROCESSO =====")
    treinar_modelo()
    api_process = iniciar_api()
    alvo = "127.0.0.1"
    run_nmap(alvo)
    classificar_resultados()
    parar_api(api_process)
    log("===== FIM DO PROCESSO =====\n")
