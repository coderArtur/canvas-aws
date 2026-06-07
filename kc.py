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

def resolver_kc(nova_aba, nome_kc, gabarito):
    nova_aba.wait_for_load_state('networkidle')
    time.sleep(3) # Aguarda o Articulate Storyline carregar todos os frames
    
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
        if btn_reiniciar.count() > 0:
            btn_reiniciar.first.dispatch_event('click')
            time.sleep(2)
    except:
        pass
        
    # --- MUDANÇA AQUI: Usar dispatch_event APENAS para o popup "Não" ---
    # O usuário confirmou que dispatch_event funciona para o popup
    try:
        botao_nao = frame.locator('button[aria-label="Não"]')
        botao_nao.dispatch_event('click')
        time.sleep(3)
    except:
        pass  # Se não aparecer o popup, segue normalmente
    # -------------------------------------------------------------------
    
    # Iniciar (Usando o .click normal que o usuário disse que funciona)
    frame.locator('div[data-acc-text="Iniciar"]').click()
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
                if texto and texto not in ["Iniciar", "ENVIAR", "Continuar", "Resultados da verificação de conhecimento"]:
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
    frame.locator('span:has-text("Resultados da verificação de conhecimento"), span:has-text("Resultados do teste de conhecimento")').wait_for(state="visible", timeout=60000)
    time.sleep(3)
    
    # Fecha a aba
    nova_aba.close()
