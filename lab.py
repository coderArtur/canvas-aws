import time

def resolver_lab(nova_aba):
    try:
        nova_aba.wait_for_load_state('networkidle', timeout=15000)
    except:
        pass
    time.sleep(3)
    
    if "terms_new" in nova_aba.url:
        nova_aba.locator('button[type="submit"]:has-text("I Agree")').click()
        try:
            nova_aba.wait_for_load_state('networkidle', timeout=15000)
        except:
            pass
        time.sleep(2)
        
    #identifica se existe o botão de Start Lab (V1 e V2) ou se não tem (V1.1)
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
        
        textareas = nova_aba.locator('textarea.voc_textarea').all()
        for txt in textareas:
            try:
                txt.fill("Ótimo")
                time.sleep(0.5)
            except:
                pass
                
        print("  Submetendo tarefa (Versão 1.1)...")
        nova_aba.locator('div#btn-submitasn:has-text("Submit")').click()
        time.sleep(2)
        
        yes_btn = nova_aba.locator('a.vocbtn-action:has-text("Yes")')
        if yes_btn.count() > 0:
            yes_btn.click()
            time.sleep(2)
            
        print("  Aguardando nota 1/1...")
        nova_aba.frame_locator('iframe[src*="grades_review"]').locator('tr#totalScore:has-text("1/1")').wait_for(state="visible", timeout=300000)
            
        print("  Lab concluído com sucesso!")
        time.sleep(3)
        nova_aba.close()
        return

    is_v1 = False
    if nova_aba.locator('i#vmstatus').count() > 0:
        is_v1 = True
        
    if not is_v1:
        print("  -> Estrutura Versão 2 do Lab detectada (Modal AWS)")

        #V2
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
        relatorio_encontrado = False
        for _ in range(60):
            if nova_aba.locator('p#report_submission_msg_box:has-text("Executed at:")').is_visible():
                time.sleep(2)
                try:
                    nova_aba.locator('#modal-table-report-submission button.close[data-dismiss="modal"]').click(timeout=3000)
                except:
                    pass
                relatorio_encontrado = True
                break
                
            try:
                if nova_aba.locator('div#gradeframe').is_visible():
                    iframe = nova_aba.frame_locator('div#gradeframe iframe[src*="grades_review"]')
                    if iframe.locator('tr#totalScore').is_visible():
                        time.sleep(2)
                        try:
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

        #V1 (Padrão Antigo - LEDs)
        print("  Aguardando VM ficar pronta (LED Verde)...")
        nova_aba.locator('i[role="status"]#vmstatus.led-green').wait_for(state="visible", timeout=1200000)
        
        print("  VM Pronta! Submetendo tarefa...")
        nova_aba.locator('div[role="button"]#btn-submitasn').click()
        time.sleep(2)
        nova_aba.locator('a.vocbtn-action:has-text("Yes")').click()
        
        print("  Aguardando nota 1/1...")
        nova_aba.frame_locator('iframe[src*="grades_review"]').locator('tr#totalScore:has-text("1/1")').wait_for(state="visible", timeout=300000)
        time.sleep(2)
        
        try:
            if nova_aba.locator('#modal-table-report-submission').is_visible():
                nova_aba.locator('#modal-table-report-submission button.close[data-dismiss="modal"]').click(timeout=3000)
                time.sleep(2)
        except:
            pass
        
        print("  Encerrando Lab...")
        nova_aba.locator('div[role="button"][aria-label="End Lab"]').click()
        time.sleep(2)
        nova_aba.locator('a.vocbtn-action:has-text("Yes")').click()
        
        print("  Aguardando término da VM (LED Vermelho)...")
        nova_aba.locator('i[role="status"]#vmstatus.led-red').wait_for(state="visible", timeout=600000)
        
    time.sleep(3)
    print("  Lab concluído com sucesso!")
    nova_aba.close()
