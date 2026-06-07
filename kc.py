import time
import re
import string
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
        
    # 1. Deixa tudo minúsculo
    texto = texto.lower()
    
    # 2. Remove todas as acentuações (á, ã, ç viram a, a, c)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    
    # # 3. Substitui qualquer pontuação (hífen, ponto, vírgula) por espaço
    # for p in string.punctuation:
    #     texto = texto.replace(p, " ")
        
    # 4. Remove espaços extras e junta tudo
    return " ".join(texto.split())

def resolver_kc_v2(nova_aba, nome_kc, gabarito):
    print("  -> Estrutura Versão 2 (Vocareum) do KC detectada")
    
    # Selecionar idioma PT-BR (Pode estar na main page ou iframe)
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

    # Aguarda um pouco extra após possível reload de idioma
    time.sleep(3)
    
    # Tenta descobrir onde as perguntas estão buscando em todos os frames
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

    # Pega apenas as respostas da tarefa atual
    match = re.search(r'\d+', nome_kc)
    chave_gabarito = match.group() if match else nome_kc
    respostas_corretas = gabarito.get(chave_gabarito, [])

    for indice, alternativas_corretas in enumerate(respostas_corretas):
        print(f"  Respondendo página/questão {indice + 1}...")
        
        # Espera carregar as opções da página atual
        time.sleep(2)
        
        # Pega todas as opções (inclusive as de outras abas/páginas escondidas)
        opcoes_na_tela = context.locator('.voc_radio_label').all()
        for opcao in opcoes_na_tela:
            # Só processa se a opção estiver visível (evita clicar em questões de outras abas)
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
                    
            if maior_score > 0.80:
                try:
                    opcao.click(timeout=3000)
                    time.sleep(0.5)
                except:
                    pass

        # Se chegamos na última resposta cadastrada para este KC, sai do loop
        if indice == len(respostas_corretas) - 1:
            print("  Última página alcançada pelo gabarito.")
            break
            
        # Senão, deve haver um botão Next
        try:
            # Como todas as abas são carregadas de uma vez, o botão Next da aba atual 
            # corresponde ao índice da pergunta atual ('indice')
            btn_next = context.locator('.btnNext')
            if btn_next.count() > indice:
                btn_next.nth(indice).click(force=True, timeout=3000)
            else:
                # Fallback pelo texto
                context.locator('a:has-text("Next")').nth(indice).click(force=True, timeout=3000)
                
            time.sleep(2)
        except Exception as e:
            print(f"  Aviso: Não conseguiu clicar no botão Next. Erro: {e}")
                
    # Submeter
    print("  Submetendo KC (Vocareum)...")
    btn_submit = nova_aba.locator('div#btn-submitasn:has-text("Submit")')
    if btn_submit.count() > 0:
        btn_submit.first.click()
        time.sleep(2)
        
    # Clicar em Yes no popup
    btn_yes = nova_aba.locator('a.vocbtn-action:has-text("Yes")')
    if btn_yes.count() > 0:
        try:
            btn_yes.first.click(timeout=3000)
        except:
            pass
            
    # Aguarda o tempo fixo solicitado pelo usuário em vez de procurar relatórios
    print("  Aguardando 15 segundos para consolidação...")
    time.sleep(15)
            
    print("  KC concluído com sucesso!")
    nova_aba.close()

def resolver_kc(nova_aba, nome_kc, gabarito):
    nova_aba.wait_for_load_state('networkidle')
    time.sleep(3) # Aguarda o Articulate Storyline carregar todos os frames
    
    # Verifica se é a versão 2 (Vocareum KC)
    btn_submit = nova_aba.locator('div#btn-submitasn:has-text("Submit")')
    if btn_submit.count() > 0:
        resolver_kc_v2(nova_aba, nome_kc, gabarito)
        return

    
    # O conteúdo interativo do KC vive dentro do frame "ScormContent" (aninhado em vários iframes)
    # Usar .frame() busca pelo nome em qualquer profundidade
    frame = nova_aba.frame(name="ScormContent")
    
    # Aguarda o frame carregar (pode demorar um pouco em conexões lentas)
    if not frame:
        time.sleep(3)
        frame = nova_aba.frame(name="ScormContent")
    
    # Verifica e clica em "Reiniciar" na tela de proteção (mobile/resume overlay) caso apareça
    try:
        btn_reiniciar = frame.locator('button.restart[aria-label="Reiniciar"]')
        # Espera no máximo 3 segundos para ver se o botão aparece
        btn_reiniciar.wait_for(state="attached", timeout=3000)
        btn_reiniciar.first.dispatch_event('click')
        time.sleep(2)
    except:
        pass
        
    # --- MUDANÇA AQUI: Usar dispatch_event APENAS para o popup "Não" ---
    # O usuário confirmou que dispatch_event funciona para o popup
    try:
        botao_nao = frame.locator('button[aria-label="Não"], button[aria-label="No"]')
        # Espera no máximo 3 segundos para ver se o popup "Não" aparece
        botao_nao.wait_for(state="attached", timeout=3000)
        botao_nao.first.dispatch_event('click')
        time.sleep(3)
    except:
        pass  # Se não aparecer o popup, segue normalmente
    # -------------------------------------------------------------------
    
    # Iniciar ou Comenzar (Usando o .click normal que o usuário disse que funciona)
    frame.locator('div[data-acc-text="Iniciar"], div[data-acc-text="Comenzar"]').click()
    time.sleep(2)
    
    # Extrai o número do nome (Ex: "2-CF- KC..." vira apenas "2")
    match = re.search(r'\d+', nome_kc)
    chave_gabarito = match.group() if match else nome_kc
    respostas_corretas = gabarito.get(chave_gabarito, [])
    
    # Exceção relatada no seu TXT para o KC 298 agrupada por questão (tela a tela)
    if "298" in nome_kc:
        respostas_corretas = [
            ["Consultorias e boletins da AWS", "Equipes de conta da AWS"], # Tela 1
            ["Guias técnicos da AWS", "Caminho de aprendizagem para auditores da AWS"], # Tela 2
            ["Consultorias e boletins da AWS"], # Tela 3 (original do gabarito)
            ["Suporte 24 horas por dia, 7 dias por semana, por telefone, chat ou e-mail", "Um technical account manager (TAM) da AWS dedicado"], # Tela 4
            ["Eles orientam os clientes durante a implantação e implementação."] # Tela 5
        ]
        
    # Agora o robô itera tela por tela (questão por questão)
    for respostas_da_questao in respostas_corretas:
        time.sleep(2) # Pequena pausa para garantir que a animação da pergunta terminou
        
        # Se for uma das questões vazias ("?")
        if len(respostas_da_questao) == 0:
            print("Questão sem gabarito! Chutando as 3 primeiras opções...")
            # Pega tudo na tela que tem data-acc-text
            opcoes = frame.locator('div[data-acc-text]').all()
            cliques = 0
            for opcao in opcoes:
                texto = opcao.get_attribute('data-acc-text')
                # Ignora os textos dos botões principais
                if texto and texto not in ["Iniciar", "Comenzar", "ENVIAR", "Continuar", "Resultados da verificação de conhecimento"]:
                    try:
                        # Tenta clicar. Se for a pergunta em si, o clique não faz nada, se for opção ele marca
                        opcao.click(timeout=500)
                        cliques += 1
                        time.sleep(0.3)
                        # Parar após 3 chutes
                        if cliques >= 3:
                            break
                    except:
                        pass
        else:
            # Clica em todas as opções corretas DAQUELA tela usando comparação inteligente
            opcoes_na_tela = frame.locator('div[data-acc-text]').all()
            
            for resposta_gabarito in respostas_da_questao:
                resposta_norm = normalizar_texto(resposta_gabarito)
                
                melhor_opcao = None
                maior_score = 0.0
                
                for opcao in opcoes_na_tela:
                    texto_opcao = opcao.get_attribute('data-acc-text')
                    # Ignorar se estiver vazio ou se for um botão de navegação
                    if not texto_opcao or texto_opcao in ["Iniciar", "ENVIAR", "Continuar", "Resultados da verificação de conhecimento"]:
                        continue
                        
                    texto_opcao_norm = normalizar_texto(texto_opcao)
                    
                    # 1. Bate perfeitamente
                    if resposta_norm == texto_opcao_norm:
                        melhor_opcao = opcao
                        maior_score = 1.0
                        break # Se achou 100% igual, não precisa olhar o resto
                        
                    # 2. Substring ou Fuzzy matching
                    # Aceita substrings se a palavra tiver pelo menos 3 letras, mas se for apenas um número, aceita com 1 dígito.
                    tamanho_minimo = 1 if resposta_norm.replace(' ', '').isdigit() else 3
                    score_substring = 0.95 if (len(resposta_norm) >= tamanho_minimo and (resposta_norm in texto_opcao_norm or texto_opcao_norm in resposta_norm)) else 0.0
                    score_fuzzy = difflib.SequenceMatcher(None, resposta_norm, texto_opcao_norm).ratio()
                    
                    score_atual = max(score_substring, score_fuzzy)
                    
                    if score_atual > maior_score:
                        maior_score = score_atual
                        melhor_opcao = opcao
                
                # Clica apenas na melhor opção encontrada para esta resposta do gabarito (se for >= 80% similar)
                if melhor_opcao and maior_score > 0.80:
                    try:
                        melhor_opcao.click(timeout=3000)
                        time.sleep(1) # Dá mais tempo para o canvas processar o clique antes de ir pra próxima
                    except:
                        pass
            
        # Clicar no botão ENVIAR da questão atual
        # Pode ter o texto "ENVIAR" ou apenas um ícone (mas sempre tem id="submit")
        frame.locator('button#submit').click()
        time.sleep(1)
        
        # Clicar em Continuar para ir para a próxima questão (Este botão também é um popup do Storyline)
        frame.locator('button:has(span:has-text("Continuar"))').dispatch_event('click')
        time.sleep(1)
        
    # Ao terminar todas as questões e sair do loop, aguarda a tela de finalização
    # Pode ser "Resultados da verificação de conhecimento" ou "Resultados do teste de conhecimento"
    # frame.locator('span:has-text("Resultados da verificação de conhecimento"), span:has-text("Resultados do teste de conhecimento")').wait_for(state="visible", timeout=60000)
    time.sleep(3)
    
    # Fecha a aba
    nova_aba.close()
