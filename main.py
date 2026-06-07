# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright
from config import OCULTAR_TELA
from login import realizar_login
from tarefas import obter_tarefas_pendentes, abrir_tarefa
from lab import resolver_lab
from kc import resolver_kc
import json

# Carrega o arquivo JSON gerado com todas as respostas do PDF
with open("gabarito.json", "r", encoding="utf-8") as f:
    gabarito = json.load(f)

def main():
    # Menu interativo no terminal
    print("===================================")
    print(" 1 - Apenas KCs")
    print(" 2 - Apenas Labs")
    print(" 3 - KCs e Labs (Recomendado)")
    print("===================================")
    escolha = input("Digite o número (pressione ENTER para 3): ").strip()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=OCULTAR_TELA)
        context = browser.new_context()
        page = context.new_page()
        
        print("\nRealizando login...")
        realizar_login(page)
        
        print("Buscando tarefas pendentes...")
        tarefas = obter_tarefas_pendentes(page)
        
        for tarefa in tarefas:
            # Lógica de filtro baseada na escolha
            if escolha == "1" and tarefa['tipo'] != "KC":
                continue
            if escolha == "2" and tarefa['tipo'] != "Lab":
                continue
                
            print(f"Resolvendo: {tarefa['nome']}")
            nova_aba = abrir_tarefa(page, tarefa['url'])
            
            # Se a tarefa foi pulada (ex: aguardando revisão), nova_aba será None
            if not nova_aba:
                continue
            
            if tarefa['tipo'] == "Lab":
                resolver_lab(nova_aba)
            else:
                resolver_kc(nova_aba, tarefa['nome'], gabarito)
                
        print("Todas as tarefas escolhidas foram concluídas!")
        browser.close()

if __name__ == "__main__":
    main()
