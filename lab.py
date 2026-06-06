import time

def resolver_lab(nova_aba):
    nova_aba.wait_for_load_state('networkidle')
    time.sleep(3)
    
    # Se aparecer os termos para aceitar
    if "terms_new" in nova_aba.url:
        nova_aba.locator('button[type="submit"]:has-text("I Agree")').click()
        nova_aba.wait_for_load_state('networkidle')
        time.sleep(2)
        
    # --- Identifica e clica no botão de Start Lab ---
    start_btn = nova_aba.locator('div[role="button"][aria-label="Start Lab"]')
    if start_btn.count() == 0:
        start_btn = nova_aba.locator('div[role="button"]:has-text("Start Lab")')
    start_btn.click()
    
    # Vamos aguardar até 4 segundos para ver se o popup modal da AWS (Versão 2) aparece na tela
    is_v2 = False
    try:
        # Na versão 2 (AWS modal), o popup de progresso fica *visível* logo após clicar no botão
        nova_aba.locator('p#report_aws_progress_box').wait_for(state="visible", timeout=10000)
        is_v2 = True
    except:
        is_v2 = False

    if is_v2:
        print("  -> Estrutura Versão 2 do Lab detectada (Modal AWS)")
        # ================================
        # VERSÃO 2 (AWS CloudFormation Modals)
        # ================================
        print("  Aguardando criação do ambiente (Isso pode demorar alguns minutos)...")
        nova_aba.locator('p#report_aws_progress_box:has-text("ready")').wait_for(state="visible", timeout=1200000) # Até 20 min
        time.sleep(2)
        
        nova_aba.locator('#modal-table-report-aws button.close[data-dismiss="modal"]').click()
        time.sleep(3)
        
        print("  Ambiente pronto! Submetendo tarefa...")
        nova_aba.locator('div[role="button"]:has-text("Submit")').click()
        time.sleep(2)
        
        nova_aba.locator('a.vocbtn-action:has-text("Yes")').click()
        
        print("  Aguardando relatório de submissão da nota...")
        nova_aba.locator('p#report_submission_msg_box:has-text("Executed at:")').wait_for(state="visible", timeout=300000)
        time.sleep(2)
        
        nova_aba.locator('#modal-table-report-submission button.close[data-dismiss="modal"]').click()
        time.sleep(2)
        
        print("  Encerrando Lab...")
        nova_aba.locator('div[role="button"]:has-text("End Lab")').click()
        time.sleep(2)
        
        nova_aba.locator('a.vocbtn-action:has-text("Yes")').click()
        
        print("  Aguardando término dos recursos na AWS...")
        nova_aba.locator('p#report_aws_msg_box:has-text("You may close this message box now")').wait_for(state="visible", timeout=600000)
        time.sleep(2)
        
        nova_aba.locator('#modal-table-report-aws button.close[data-dismiss="modal"]').click()
        
    else:
        print("  -> Estrutura Versão 1 do Lab detectada (VM Status LEDs)")
        print("  Aguardando VM ficar pronta (LED Verde)...")
        nova_aba.locator('i[role="status"]#vmstatus.led-green').wait_for(state="visible", timeout=1200000)
        # Submeter e aceitar popup genérico
        print("  VM Pronta! Submetendo tarefa...")
        nova_aba.locator('div[role="button"]#btn-submitasn').click()
        time.sleep(2)
        nova_aba.locator('a.vocbtn-action:has-text("Yes")').click()
        
        # Aguardar nota 1/1
        print("  Aguardando nota 1/1...")
        nova_aba.frame_locator('#panel3-iframe').locator('tr#totalScore:has-text("1/1")').wait_for(state="visible", timeout=300000)
        time.sleep(2)
        
        # Encerrar Lab e aceitar popup genérico
        print("  Encerrando Lab...")
        nova_aba.locator('div[role="button"][aria-label="End Lab"]').click()
        time.sleep(2)
        nova_aba.locator('a.vocbtn-action:has-text("Yes")').click()
        
        print("  Aguardando término da VM (LED Vermelho)...")
        nova_aba.locator('i[role="status"]#vmstatus.led-red').wait_for(state="visible", timeout=600000)
        
    time.sleep(3)
    print("  Lab concluído com sucesso!")
    nova_aba.close()
