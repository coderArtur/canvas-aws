import time
import re
import unicodedata
import difflib

def normalizar_texto(texto):
    if not texto:
        return ""
        
    texto = str(texto).strip()
    if texto.endswith("..."):
        texto = texto[:-3]
    elif texto.endswith(".."):
        texto = texto[:-2]
        
    texto = texto.lower()
    
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    
    return " ".join(texto.split())

def resolver_kc_v2(nova_aba, nome_kc, gabarito):
    print("  -> Estrutura Versão 2 (Vocareum) do KC detectada")
    
    try:
        lang_select = nova_aba.locator('select#localeLangReadmeSelect')
        if lang_select.count() > 0:
            lang_select.select_option('pt-br')
            time.sleep(2)
        else:
            lang_select_frame = nova_aba.frame_locator('iframe#panel3-iframe').locator('select#localeLangReadmeSelect')
            if lang_select_frame.count() > 0:
                lang_select_frame.select_option('pt-br')
                time.sleep(2)
    except:
        pass

    time.sleep(3)
    
    context = None
    print("  Procurando perguntas nos frames disponíveis...")
    for frame in nova_aba.frames:
        if frame.locator('.voc_radio_label').count() > 0:
            print(f"  -> Perguntas encontradas no frame: {frame.name} ({frame.url})")
            context = frame
            break
            
    if not context:
        print("  -> Perguntas NÃO encontradas em nenhum frame. Usando página principal como fallback.")
        context = nova_aba

    match = re.search(r'\d+', nome_kc)
    chave_gabarito = match.group() if match else nome_kc
    respostas_corretas = gabarito.get(chave_gabarito, [])

    for indice, alternativas_corretas in enumerate(respostas_corretas):
        print(f"  Respondendo página/questão {indice + 1}...")
        
        time.sleep(2)
        
        opcoes_na_tela = context.locator('.voc_radio_label').all()
        for opcao in opcoes_na_tela:
            if not opcao.is_visible():
                continue
                
            texto_opcao = normalizar_texto(opcao.text_content())
            maior_score = 0
            
            for correto_raw in alternativas_corretas:
                correto = normalizar_texto(correto_raw)
                if not correto:
                    continue
                    
                if correto in texto_opcao or texto_opcao in correto:
                    score_substring = 1.0
                else:
                    score_substring = 0.0
                    
                score_fuzzy = difflib.SequenceMatcher(None, texto_opcao, correto).ratio()
                score_atual = max(score_substring, score_fuzzy)
                
                if score_atual > maior_score:
                    maior_score = score_atual
                    
            if maior_score > 0.75:
                try:
                    opcao.click(timeout=3000)
                    time.sleep(0.5)
                except:
                    pass

        if indice == len(respostas_corretas) - 1:
            print("  Última página alcançada pelo gabarito.")
            break
            
        try:
            btn_next = context.locator('.btnNext')
            if btn_next.count() > indice:
                btn_next.nth(indice).click(force=True, timeout=3000)
            else:
                context.locator('a:has-text("Next")').nth(indice).click(force=True, timeout=3000)
                
            time.sleep(2)
        except Exception as e:
            print(f"  Aviso: Não conseguiu clicar no botão Next. Erro: {e}")
                
    print("  Submetendo KC (Vocareum)...")
    btn_submit = nova_aba.locator('div#btn-submitasn:has-text("Submit")')
    if btn_submit.count() > 0:
        btn_submit.first.click()
        time.sleep(2)
        
    btn_yes = nova_aba.locator('a.vocbtn-action:has-text("Yes")')
    if btn_yes.count() > 0:
        try:
            btn_yes.first.click(timeout=3000)
        except:
            pass
            
    print("  Aguardando 15 segundos para consolidação...")
    time.sleep(15)
            
    print("  KC concluído com sucesso!")
    nova_aba.close()

def resolver_kc(nova_aba, nome_kc, gabarito):
    try:
        nova_aba.wait_for_load_state('networkidle', timeout=15000)
    except:
        pass
    time.sleep(3) 
    
    btn_submit = nova_aba.locator('div#btn-submitasn:has-text("Submit")')
    if btn_submit.count() > 0:
        resolver_kc_v2(nova_aba, nome_kc, gabarito)
        return

    frame = nova_aba.frame(name="ScormContent")
    
    if not frame:
        time.sleep(3)
        frame = nova_aba.frame(name="ScormContent")
    
    try:
        btn_reiniciar = frame.locator('button.restart[aria-label="Reiniciar"]')
        btn_reiniciar.wait_for(state="attached", timeout=3000)
        btn_reiniciar.first.dispatch_event('click')
        time.sleep(2)
    except:
        pass
        
    try:
        botao_nao = frame.locator('button[aria-label="Não"], button[aria-label="No"]')
        botao_nao.wait_for(state="attached", timeout=3000)
        botao_nao.first.dispatch_event('click')
        time.sleep(3)
    except:
        pass 
    
    frame.locator('div[data-acc-text="Iniciar"], div[data-acc-text="Comenzar"]').click()
    time.sleep(2)
    
    match = re.search(r'\d+', nome_kc)
    chave_gabarito = match.group() if match else nome_kc
    respostas_corretas = gabarito.get(chave_gabarito, [])
    

    for respostas_da_questao in respostas_corretas:
        time.sleep(2) 
        
        if len(respostas_da_questao) == 0:
            print("Questão sem gabarito! Chutando as 3 primeiras opções...")
            opcoes = frame.locator('div[data-acc-text]').all()
            cliques = 0
            for opcao in opcoes:
                texto = opcao.get_attribute('data-acc-text')
                if texto:
                    texto_lower = texto.lower()
                    ignorar = ["iniciar", "comenzar", "enviar", "continuar", "resultados da verificação de conhecimento"]
                    if texto_lower not in ignorar and "navega" not in texto_lower and "teclado" not in texto_lower:
                        try:
                            opcao.click(timeout=500)
                            cliques += 1
                            time.sleep(0.3)
                            if cliques >= 3:
                                break
                        except:
                            pass
        else:
            opcoes_na_tela = frame.locator('div[data-acc-text]').all()
            
            for resposta_gabarito in respostas_da_questao:
                resposta_norm = normalizar_texto(resposta_gabarito)
                
                melhor_opcao = None
                maior_score = 0.0
                
                for opcao in opcoes_na_tela:
                    texto_opcao = opcao.get_attribute('data-acc-text')
                    if not texto_opcao:
                        continue
                        
                    texto_lower = texto_opcao.lower()
                    ignorar = ["iniciar", "comenzar", "enviar", "continuar", "resultados da verificação de conhecimento"]
                    if texto_lower in ignorar or "navega" in texto_lower or "teclado" in texto_lower:
                        continue
                        
                    texto_opcao_norm = normalizar_texto(texto_opcao)
                    
                    if resposta_norm == texto_opcao_norm:
                        melhor_opcao = opcao
                        maior_score = 1.0
                        break 
                        
                    tamanho_minimo = 1 if resposta_norm.replace(' ', '').isdigit() else 3
                    score_substring = 0.95 if (len(resposta_norm) >= tamanho_minimo and (resposta_norm in texto_opcao_norm or texto_opcao_norm in resposta_norm)) else 0.0
                    score_fuzzy = difflib.SequenceMatcher(None, resposta_norm, texto_opcao_norm).ratio()
                    
                    score_atual = max(score_substring, score_fuzzy)
                    
                    if score_atual > maior_score:
                        maior_score = score_atual
                        melhor_opcao = opcao
                
                if melhor_opcao and maior_score > 0.75:
                    try:
                        melhor_opcao.click(timeout=3000)
                        time.sleep(1)
                    except:
                        pass
            
        try:
            frame.locator('button#submit').click(timeout=3000)
            time.sleep(1)
        except:
            pass
        
        try:
            frame.locator('button:has(span:has-text("Continuar"))').dispatch_event('click', timeout=5000)
        except:
            try:
                frame.locator('div[data-acc-text="Continuar"]').first.click(timeout=3000)
            except:
                pass
        time.sleep(1)
        
    # frame.locator('span:has-text("Resultados da verificação de conhecimento"), span:has-text("Resultados do teste de conhecimento")').wait_for(state="visible", timeout=60000)
    time.sleep(3)
    
    nova_aba.close()
