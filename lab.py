def resolver_lab(nova_aba):
    nova_aba.wait_for_load_state('networkidle')
    
    # Se aparecer os termos para aceitar
    if "terms_new" in nova_aba.url:
        nova_aba.locator('button[type="submit"]:has-text("I Agree")').click()
        nova_aba.wait_for_load_state('networkidle')
        
    # Iniciar Lab e aguardar LED verde
    nova_aba.locator('div[role="button"][aria-label="Start Lab"]').click()
    nova_aba.locator('i[role="status"]#vmstatus.led-green').wait_for(state="visible", timeout=600000)
    
    # Submeter e aceitar popup
    nova_aba.locator('div[role="button"]#btn-submitasn').click()
    nova_aba.locator('//div[@class="modal-footer"]/a[1]').click()
    
    # Aguardar nota 1/1
    nova_aba.locator('//tr[@id="totalScore"]/td[last()]:has-text("1/1")').wait_for(state="visible", timeout=120000)
    
    # Encerrar Lab e aceitar popup
    nova_aba.locator('div[role="button"][aria-label="End Lab"]').click()
    nova_aba.locator('//div[@class="modal-footer"]/a[1]').click()
    
    # Aguardar LED vermelho para garantir encerramento
    nova_aba.locator('i[role="status"]#vmstatus.led-red').wait_for(state="visible", timeout=600000)
    
    # Fecha a aba para retornar à pagina principal e continuar o script
    nova_aba.close()
