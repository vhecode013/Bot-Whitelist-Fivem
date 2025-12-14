# 🤖 Bot de Whitelist FiveM — Vhe Code RP

Bot de Discord desenvolvido em **Python (discord.py 2.4)** para servidores **FiveM RP**, com sistema completo de **Whitelist automatizada**, **logs avançados**, **entrada/saída de membros**, **painel persistente**, **slash commands** e **integração com banco de dados (MariaDB)**.



## ✨ Funcionalidades

### 📜 Sistema de Whitelist Automatizado
- Painel persistente com botão **“📜 Iniciar Whitelist”**
- Criação automática de **canal privado**
- Coleta de nome completo e ID da cidade
- Questionário com **10 perguntas de RP**
- Respostas por **botões (A/B/C/D)**
- Tempo limite de **20 minutos**
- Correção automática
- Pontuação mínima configurável
- Aprovação automática com cargo
- Atualização direta no banco de dados
- Canal apagado automaticamente após **1 minuto**



### 👮 Comandos de Staff
- `/wl <id>` → Aprova whitelist manualmente
- `/remwl <id>` → Remove whitelist manualmente
- Restrito por cargo
- Respostas **ephemeral**



### 🧾 Sistema Avançado de Logs
- Mensagens apagadas e editadas
- Entrada e saída de membros
- Alteração de cargos e nick
- Logs de whitelist
- Proteção anti-flood
- Embeds padronizados



### 👋 Entrada e Saída de Membros
- Mensagem automática de boas-vindas
- Mensagem automática de saída
- Cargo automático ao entrar
- Logs detalhados



## 📁 Estrutura do Projeto

```
bot/
│
├─ bot.py
├─ requirements.txt
│
├─ cogs/
│  ├─ entry_exit.py
│  ├─ logs.py
│  └─ whitelist.py
│
├─ utils/
│  ├─ env.py
│  ├─ database.py
│  ├─ wl_questions.py
│  ├─ wl_session.py
│  └─ wl_views.py
│
└─ .env
```


## ⚙️ Requisitos
- Python 3.10+
- MariaDB / MySQL
- Bot criado no Discord Developer Portal


## 📦 Instalação

```bash
git clone https://github.com/seu-repositorio/bot-whitelist-fivem.git
cd bot-whitelist-fivem
pip install -r requirements.txt
```



## 🔐 Configuração (.env)

```env
DISCORD_TOKEN=
DISCORD_APP_ID=

ENTRADA_CHANNEL_ID=
SAIDA_CHANNEL_ID=
LOG_CHANNEL_ID=

AUTO_ROLE_ID=

FOOTER_NOME=Desenvolvido por Vhe Code
FOOTER_LOGO=
BANNER_URL=

WL_CATEGORY_ID=
WL_PAINEL_CHANNEL_ID=
WL_APPROVED_ROLE_ID=
WL_STAFF_ROLE_ID=
WL_RESULT_CHANNEL=
WL_LOG_CHANNEL_ID=
WL_MIN_SCORE=60

DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=
DB_PORT=
```



## ▶️ Executar o Bot

```bash
python bot.py
```



## 📄 Licença

Todos os direitos reservados © **Vhe Code**
