# AWS Canvas Automator 🤖

Bem-vindo ao **AWS Canvas Automator**! Este é um robô criado para automatizar a resolução das suas tarefas no Canvas da AWS (como os laboratórios Vocareum e os Knowledge Checks).

Se você nunca usou programação antes, não se preocupe! Siga este passo a passo detalhado e o seu robô estará rodando em poucos minutos.

---

## 🚀 O que este robô faz?
Ele acessa sua conta do Canvas da AWS e procura por tarefas pendentes, tarefas que já possuem notas ele irá ignorar. 
- **Knowledge Checks (KCs)**: O robô usa um gabarito inteligente. Ele lê a questão, compara com as respostas conhecidas, e marca a opção correta. Se ele não souber a resposta, ele dá chutes calculados!
- **Laboratórios (Labs)**: O robô entra nos laboratórios (tanto os antigos quanto a nova versão do Vocareum), inicia as máquinas virtuais, aguarda elas ligarem, envia para avaliação, aguarda a sua nota 1/1, e encerra o lab sozinho.

Ele faz tudo isso sozinho enquanto você pode tomar um café. ☕

---

## 🛠️ Pré-requisitos
Antes de começar, você precisa ter duas coisas instaladas no seu computador:
1. **Python**: A linguagem de programação que roda o robô. [Baixe aqui](https://www.python.org/downloads/) (Na instalação do Windows, **não esqueça** de marcar a caixinha `"Add Python to PATH"`).
2. **Git**: Para baixar os arquivos. [Baixe aqui](https://git-scm.com/downloads).

---

## ⚙️ Passo a Passo de Instalação

Abra o seu terminal (no Windows, procure por "Prompt de Comando" ou "PowerShell"; no Linux, abra o seu Terminal).

### 1. Baixe o projeto para o seu computador
Crie uma pasta para o projeto, entre nela e execute os comandos abaixo:
```bash
git clone https://github.com/coderArtur/canvas-aws.git
cd canvas-aws
```

### 2. Crie um Ambiente Virtual (Recomendado)
O ambiente virtual isola as instalações desse projeto para não bagunçar o seu computador.

**No Windows:**
```bash
py -m venv .venv
.venv\Scripts\activate
```

**No Linux ou Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
*(Você saberá que deu certo quando a palavra `(.venv)` aparecer no começo do seu terminal)*

### 3. Instale as Bibliotecas
Essas são as ferramentas que o robô precisa para funcionar (Playwright, carregador de senhas, etc).
```bash
pip install -r requirements.txt
```

### 4. Instale o Navegador do Robô
O Playwright (o motor do robô) precisa baixar uma versão especial do navegador (Chromium) para ele navegar no Canvas.
```bash
playwright install chromium
```

---

## 🔐 Configuração da sua Conta (Importante!)

O robô precisa saber como fazer login no seu Canvas. Nós mantemos isso seguro usando um arquivo oculto chamado `.env`.

1. Na pasta do projeto, você verá um arquivo chamado `.env.example`.
2. **Faça uma cópia** desse arquivo e renomeie a cópia para apenas `.env` (sem nenhum nome antes do ponto).
3. Abra o arquivo `.env` no Bloco de Notas (ou qualquer editor) e coloque o seu e-mail e sua senha do Canvas:

```env
EMAIL=seu_email_real@gmail.com
SENHA=sua_senha_secreta
```

*(Fique tranquilo: O arquivo `.env` é ignorado pelo Git e nunca será enviado para a internet. Fica apenas no seu computador).*

---

## ▶️ Como Rodar o Robô

Tudo pronto! Sempre que quiser colocar o robô para trabalhar, abra o terminal na pasta do projeto (**lembre-se de ativar o ambiente virtual do passo 2**) e digite:

**No Windows:**
```bash
py main.py
```

**No Linux ou Mac:**
```bash
python3 main.py
```

### Menu de Opções
O robô vai iniciar e exibir um menu no terminal:
```text
===================================
 1 - Apenas KCs
 2 - Apenas Labs
 3 - KCs e Labs (Recomendado)
===================================
Digite o número (pressione ENTER para 3):
```
É só digitar o que você quer que ele resolva e apertar a tecla `Enter`.
A partir daí, relaxe e acompanhe pelo terminal os avisos dele resolvendo e encerrando as suas tarefas! 🎉

---

## ⚠️ Avisos Finais
- **O robô ignora tarefas aguardando revisão do professor**: Se ele detectar que a tarefa já foi respondida e está com status "PRÓXIMO: Revisão de feedback", ele inteligentemente pulará a tarefa para não bagunçar algo que você já enviou.
- **Não feche o terminal**: Enquanto o robô trabalha, deixe a janelinha do terminal preta aberta. Se você fechá-la, o robô morre junto.
- **Alterar o Modo Silencioso**: Por padrão, o robô trabalha escondido. Se você quiser *ver* a janela do navegador abrindo e o robô clicando nas coisas, basta abrir o arquivo `config.py` e trocar `OCULTAR_TELA = False` para `OCULTAR_TELA = True`. (Isso é útil se você quiser ver a mágica acontecendo).

Boa sorte com seus estudos na AWS! ☁️
