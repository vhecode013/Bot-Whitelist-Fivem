import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------
# Função auxiliar
# ---------------------------------------------------------
def get_int(name: str, default: int = 0) -> int:
    try:
        return int(os.getenv(name, default))
    except:
        return default


# ---------------------------------------------------------
# Canais principais
# ---------------------------------------------------------
ENTRADA_CHANNEL_ID = get_int("ENTRADA_CHANNEL_ID")
SAIDA_CHANNEL_ID = get_int("SAIDA_CHANNEL_ID")
LOG_CHANNEL_ID = get_int("LOG_CHANNEL_ID")

# Cargo automático na entrada
AUTO_ROLE_ID = get_int("AUTO_ROLE_ID")

# Branding
FOOTER_NOME = os.getenv("FOOTER_NOME", "Vhe Code Roleplay")
FOOTER_LOGO = os.getenv("FOOTER_LOGO", None)
BANNER_URL = os.getenv("BANNER_URL", None)

# ---------------------------------------------------------
# SISTEMA DE WHITELIST
# ---------------------------------------------------------
WL_CATEGORY_ID = get_int("WL_CATEGORY_ID")
WL_PAINEL_CHANNEL_ID = get_int("WL_PAINEL_CHANNEL_ID")
WL_APROVADO_ROLE_ID = get_int("WL_APROVADO_ROLE_ID")
WL_STAFF_ROLE_ID = get_int("WL_STAFF_ROLE_ID")
WL_LOG_CHANNEL_ID = get_int("WL_LOG_CHANNEL_ID")

# Nota mínima para aprovação
WL_MIN_SCORE = get_int("WL_MIN_SCORE", 60)

# ---------------------------------------------------------
# MYSQL / MARIADB
# ---------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = get_int("DB_PORT", 3306)
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
