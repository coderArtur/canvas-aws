import time

def resolver_lab(nova_aba):
    nova_aba.wait_for_load_state('networkidle')
    time.sleep(3)
    
    # Se aparecer os termos para aceitar
    if "terms_new" in nova_aba.url:
        nova_aba.locator('button[type="submit"]:has-text("I Agree")').click()
        nova_aba.wait_for_load_state('networkidle')
        time.sleep(2)
        
    # --- Identifica se existe o botão de Start Lab (V1 e V2) ou se não tem (V1.1) ---
    start_btn1 = nova_aba.locator('div[role="button"][aria-label="Start Lab"]')
    start_btn2 = nova_aba.locator('div[role="button"]:has-text("Start Lab")')
    
    is_v1_1 = False
    if start_btn1.count() > 0:
        start_btn1.click()
    elif start_btn2.count() > 0:
        start_btn2.click()
    else:
        is_v1_1 = True
        
    if is_v1_1:
        print("  -> Estrutura Versão 1.1 do Lab detectada (Sem Start Lab, apenas Questionário)")
        
        # Preencher todas as textareas da tela com "Ótimo"
        textareas = nova_aba.locator('textarea.voc_textarea').all()
        for txt in textareas:
            try:
                txt.fill("Ótimo")
                time.sleep(0.5)
            except:
                pass
                
        # Clicar em submit
        print("  Submetendo tarefa (Versão 1.1)...")
        nova_aba.locator('div#btn-submitasn:has-text("Submit")').click()
        time.sleep(2)
        
        # Confirma no popup (se existir)
        yes_btn = nova_aba.locator('a.vocbtn-action:has-text("Yes")')
        if yes_btn.count() > 0:
            yes_btn.click()
            time.sleep(2)
            
        # Aguardar nota 1/1 (V1.1 carrega em iframe sem ID no grades-panel)
        print("  Aguardando nota 1/1...")
        nova_aba.frame_locator('iframe[src*="grades_review"]').locator('tr#totalScore:has-text("1/1")').wait_for(state="visible", timeout=300000)
            
        print("  Lab concluído com sucesso!")
        time.sleep(3)
        nova_aba.close()
        return

    # Vamos detectar se é V1 ou V2 usando a presença do ícone de status (LED) exclusivo da V1
    # O vmstatus (verde/amarelo/vermelho) fica visível na tela o tempo todo na versão 1
    is_v1 = False
    if nova_aba.locator('i#vmstatus').count() > 0:
        is_v1 = True
        
    if not is_v1:
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
        relatorio_encontrado = False
        for _ in range(60): # 60 iterações de 5s = 5 minutos no total
            # Possibilidade 1: Popup "Executed at:"
            if nova_aba.locator('p#report_submission_msg_box:has-text("Executed at:")').is_visible():
                time.sleep(2)
                try:
                    # Fecha o popup de submissão
                    nova_aba.locator('#modal-table-report-submission button.close[data-dismiss="modal"]').click(timeout=3000)
                except:
                    pass
                relatorio_encontrado = True
                break
                
            # Possibilidade 2: Novo painel lateral (gradeframe)
            try:
                if nova_aba.locator('div#gradeframe').is_visible():
                    iframe = nova_aba.frame_locator('div#gradeframe iframe[src*="grades_review"]')
                    # Quando a tabela com a nota aparecer, sabemos que terminou
                    if iframe.locator('tr#totalScore').is_visible():
                        time.sleep(2)
                        try:
                            # Fecha o painel lateral no botão de menos (-)
                            nova_aba.locator('div#gradeframehide').click(timeout=3000)
                        except:
                            pass
                        relatorio_encontrado = True
                        break
            except:
                pass
                
            time.sleep(5)
            
        if not relatorio_encontrado:
            print("  Aviso: Tempo limite esgotado aguardando o relatório, prosseguindo com o encerramento...")
        
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
        
        # Submeter e aceitar popup genérico
        print("  VM Pronta! Submetendo tarefa...")
        nova_aba.locator('div[role="button"]#btn-submitasn').click()
        time.sleep(2)
        nova_aba.locator('a.vocbtn-action:has-text("Yes")').click()
        
        # Aguardar nota 1/1
        print("  Aguardando nota 1/1...")
        nova_aba.frame_locator('iframe[src*="grades_review"]').locator('tr#totalScore:has-text("1/1")').wait_for(state="visible", timeout=300000)
        time.sleep(2)
        
        # Fecha o popup de submissão caso ele tenha aparecido na V1 (para não bloquear o clique no End Lab)
        try:
            if nova_aba.locator('#modal-table-report-submission').is_visible():
                nova_aba.locator('#modal-table-report-submission button.close[data-dismiss="modal"]').click(timeout=3000)
                time.sleep(2)
        except:
            pass
        
        # Encerrar Lab e aceitar popup genérico
        print("  Encerrando Lab...")
        nova_aba.locator('div[role="button"][aria-label="End Lab"]').click()
        time.sleep(2)
        nova_aba.locator('a.vocbtn-action:has-text("Yes")').click()
        
        print("  Aguardando término da VM (LED Vermelho)...")
        nova_aba.locator('i[role="status"]#vmstatus.led-red').wait_for(state="visible", timeout=600000)
        
    time.sleep(3)
    # Fecha a aba para retornar à pagina principal e continuar o script
    print("  Lab concluído com sucesso!")
    nova_aba.close()
