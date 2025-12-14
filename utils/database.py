import aiomysql
import os
from utils.env import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Conecta ao MariaDB usando um pool — SEMPRE selecionando o banco correto."""
        if self.pool is None:
            self.pool = await aiomysql.create_pool(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                db=DB_NAME,  # <<<<<<<<<< AQUI É O PONTO CRÍTICO
                autocommit=True,
                minsize=1,
                maxsize=5
            )

    async def set_whitelist(self, user_id: int, status: int):
        """Atualiza whitelist de um ID no vrp_users."""
        await self.connect()

        sql = "UPDATE vrp_users SET whitelist = %s WHERE id = %s"

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, (status, user_id))


# Instância global
db = Database()
