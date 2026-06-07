from config import URL_ATIVIDADES, BASE_URL
import time
import re

def obter_tarefas_pendentes(page):
    tarefas = []
    page.goto(URL_ATIVIDADES)
    page.wait_for_load_state('networkidle')
    
    # Ordenar por Módulo para respeitar a linha de tempo do curso
    dropdown = page.locator('input#assignment_sort_order_select_menu')
    if dropdown.count() > 0:
        # Só vai clicar se já não estiver ordenado por Módulo
        if dropdown.input_value() != "Módulo":
            print("Alterando a ordenação das tarefas para 'Módulo'...")
            dropdown.click()
            time.sleep(1) # Aguarda a lista suspensa (dropdown) abrir na tela
            
            # Busca a opção exata escrita "Módulo" dentro da lista e clica
            page.get_by_role("option", name="Módulo", exact=True).click()
            
            # Clica no botão Aplicar
            page.locator('button#apply_select_menus').click()
            
            # Como o botão recarrega a página, esperamos a rede acalmar novamente
            page.wait_for_load_state('networkidle')
            print("Aguardando 10 segundos para a tabela do Canvas renderizar...")
            time.sleep(10) # 10 segundos de segurança para a tabela gigante aparecer
            
    linhas = page.locator('//tbody/tr[contains(@class,"student_")]').all()
    
    for linha in linhas:
        nota_span = linha.locator('//td[@class="assignment_score"]//span[@class="grade"]')
        if nota_span.count() > 0 and "-" in nota_span.inner_text():
            link = linha.locator('th a')
            nome_tarefa = link.inner_text()
            href = link.get_attribute("href")
            
            if "Lab" in nome_tarefa:
                tipo = "Lab"
            elif "KC" in nome_tarefa or re.search(r'\d+', nome_tarefa):
                tipo = "KC"
            else:
                # Se não tem "Lab", nem "KC" e nem sequer um número de identificação, ignore!
                print(f"Ignorando tarefa desconhecida: {nome_tarefa}")
                continue
                
            tarefas.append({"nome": nome_tarefa, "url": BASE_URL + href, "tipo": tipo})
            
    return tarefas

def abrir_tarefa(page, url_tarefa):
    page.goto(url_tarefa)
    
    # Espera o carregamento da página
    page.wait_for_load_state('networkidle')
    import time
    time.sleep(3)
    
    # Verifica se a tarefa já foi enviada e está aguardando revisão do feedback do instrutor
    status_locator = page.locator('div[data-testid="submission-workflow-tracker-subtitle"]')
    if status_locator.count() > 0:
        texto_status = status_locator.first.inner_text().strip()
        if texto_status == "PRÓXIMO: Revisão de feedback":
            print("  -> Tarefa já enviada e aguardando revisão. Pulando...")
            return None
    
    with page.context.expect_page() as nova_aba_info:
        # O botão está DENTRO do iframe com class "tool_launch"
        iframe = page.frame_locator('iframe.tool_launch')
        iframe.locator('div.load_tab button').click(force=True)
        
    return nova_aba_info.value
