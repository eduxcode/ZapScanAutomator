# -*- coding: utf-8 -*-
import subprocess
import argparse
import json
import os
from jinja2 import Template

# Configurações
ZAP_PATH = r"C:\Program Files\ZAP\Zed Attack Proxy\zap-2.16.0.jar"  # Caminho para o ZAP no Windows
TARGET_URL = "http://testhtml5.vulnweb.com."  # URL alvo do scan
REPORT_DIR = "reports"
TEMPLATE_DIR = "templates"

# Executa o scan com OWASP ZAP
def run_zap_scan(target):
    print(f"Iniciando scan no alvo: {target}")
    command = f'java -jar "{ZAP_PATH}" -cmd -quickurl {target} -quickout {REPORT_DIR}/report.json'
    subprocess.run(command, shell=True)
    print("Scan concluído!")

def parse_args():
    parser = argparse.ArgumentParser(description="Automatizador de Scan com OWASP ZAP")
    parser.add_argument("-u", "--url", help="URL alvo do scan", required=True)
    parser.add_argument("-o", "--output", help="Diretório de saída", default="reports")
    return parser.parse_args()

def get_target_url(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# Processa o relatório JSON
def process_report():
    report_path = os.path.join(REPORT_DIR, "report.json")
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        #Acessa as vunerabilidades
        if "site" in report and len(report["site"]) > 0 and "alerts" in report["site"][0]:
            vulnerabilities = report["site"][0]["alerts"]

            # Converter riskcode para string e armazenar todas as vulnerabilidades
            for v in vulnerabilities:
                v["riskcode"] = str(v["riskcode"])  # Garante que o riskcode é string

            print(f"Total de vulnerabilidades encontradas: {len(vulnerabilities)}")
            return vulnerabilities

        else:
            print("Erro: Nenhum site ou vulnerabilidade encontrada no relatório.")
            return []
    except FileNotFoundError:
        print("Erro: Relatório não encontrado. Verifique se o scan foi executado corretamente.")
        return []
    except KeyError as e:
        print(f"Erro: Estrutura do JSON inesperada. Chave não encontrada: {e}")
        return []

# Gera um relatório HTML
def generate_html_report(vulnerabilities):
    template_path = os.path.join(TEMPLATE_DIR, "report_template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()


    # Conta vulnerabilidades por severidade
    severity_counts = {
        "Informacional": sum(1 for v in vulnerabilities if v["riskcode"] == "0"),
        "Baixo": sum(1 for v in vulnerabilities if v["riskcode"] == "1"),
        "Médio": sum(1 for v in vulnerabilities if v["riskcode"] == "2"),
        "Alto": sum(1 for v in vulnerabilities if v["riskcode"] == "3"),
        "Crítico": sum(1 for v in vulnerabilities if v["riskcode"] == "4")
    }

    template = Template(template_content)
    html_report = template.render(
        vulnerabilities=vulnerabilities,
        severity_counts=severity_counts
    )


    report_path = os.path.join(REPORT_DIR, "report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_report)
    print(f"Relatório HTML gerado: {report_path}")

# Função principal
def main():
    # Verifica se o diretório de relatórios existe
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

    # Executa o scan e gera o relatório
    run_zap_scan(TARGET_URL)
    vulnerabilities = process_report()
    generate_html_report(vulnerabilities)

if __name__ == "__main__":
    main()
