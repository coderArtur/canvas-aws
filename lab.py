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
    
    # Vamos esperar um pouquinho para ver qual elemento reage na tela
    time.sleep(3)
    
    is_v2 = False
    try:
        # Na versão 2 (AWS modal), o popup de progresso aparece logo após clicar no botão
        if nova_aba.locator('p#report_aws_progress_box').count() > 0:
            is_v2 = True
    except:
        pass

    if is_v2:
        print("  -> Estrutura Versão 2 do Lab detectada (Modal AWS)")
        # ================================
        # VERSÃO 2 (AWS CloudFormation Modals)
        # ================================
        print("  Aguardando criação do ambiente (Isso pode demorar alguns minutos)...")
        nova_aba.locator('p#report_aws_progress_box:has-text("ready")').wait_for(state="visible", timeout=1200000) # Até 20 min
        time.sleep(2)
        
        # Fecha o popup "Start Lab"
        nova_aba.locator('#modal-table-report-aws button.close[data-dismiss="modal"]').click()
        time.sleep(3) # Pausa de 3 segundos antes de submeter
        
        # Submeter
        print("  Ambiente pronto! Submetendo tarefa...")
        nova_aba.locator('div[role="button"]:has-text("Submit")').click()
        time.sleep(2)
        
        # Confirmar submissão "Yes"
        nova_aba.locator('a.vocbtn-action:has-text("Yes")').click()
        
        # Aguardar relatório de submissão
        print("  Aguardando relatório de submissão da nota...")
        nova_aba.locator('p#report_submission_msg_box:has-text("Executed at:")').wait_for(state="visible", timeout=300000)
        time.sleep(2)
        
        # Fecha o popup de submissão
        nova_aba.locator('#modal-table-report-submission button.close[data-dismiss="modal"]').click()
        time.sleep(2)
        
        # Encerrar Lab
        print("  Encerrando Lab...")
        nova_aba.locator('div[role="button"]:has-text("End Lab")').click()
        time.sleep(2)
        
        # Confirmar encerramento "Yes"
        nova_aba.locator('a.vocbtn-action:has-text("Yes")').click()
        
        # Aguardar finalização dos recursos AWS
        print("  Aguardando término dos recursos na AWS...")
        nova_aba.locator('p#report_aws_msg_box:has-text("You may close this message box now")').wait_for(state="visible", timeout=600000)
        time.sleep(2)
        
        # Fecha o popup final de encerramento
        nova_aba.locator('#modal-table-report-aws button.close[data-dismiss="modal"]').click()
        
    else:
        print("  -> Estrutura Versão 1 do Lab detectada (VM Status LEDs)")
        # ================================
        # VERSÃO 1 (Padrão Antigo - LEDs)
        # ================================
        print("  Aguardando VM ficar pronta (LED Verde)...")
        nova_aba.locator('i[role="status"]#vmstatus.led-green').wait_for(state="visible", timeout=1200000)
        time.sleep(2)
        
        # Submeter e aceitar popup genérico
        print("  VM Pronta! Submetendo tarefa...")
        nova_aba.locator('div[role="button"]#btn-submitasn').click()
        time.sleep(2)
        nova_aba.locator('//div[@class="modal-footer"]/a[1]').click()
        
        # Aguardar nota 1/1
        print("  Aguardando nota 1/1...")
        nova_aba.locator('//tr[@id="totalScore"]/td[last()]:has-text("1/1")').wait_for(state="visible", timeout=300000)
        time.sleep(2)
        
        # Encerrar Lab e aceitar popup genérico
        print("  Encerrando Lab...")
        nova_aba.locator('div[role="button"][aria-label="End Lab"]').click()
        time.sleep(2)
        nova_aba.locator('//div[@class="modal-footer"]/a[1]').click()
        
        # Aguardar LED vermelho para garantir encerramento
        print("  Aguardando término da VM (LED Vermelho)...")
        nova_aba.locator('i[role="status"]#vmstatus.led-red').wait_for(state="visible", timeout=600000)
        
    time.sleep(3)
    # Fecha a aba para retornar à pagina principal e continuar o script
    print("  Lab concluído com sucesso!")
    nova_aba.close()
