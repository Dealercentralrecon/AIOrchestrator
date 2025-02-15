import asyncpg
from . import DatabaseManager

class PostgresManager(DatabaseManager):
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.dsn)
        await self._create_tables()

    async def _create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS code_versions (
                    id SERIAL PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    hash TEXT NOT NULL,
                    code TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_agent_hash 
                ON code_versions (agent_id, hash);
            ''')

    async def store_code_version(self, agent_id: str, code_hash: str, code: str):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO code_versions (agent_id, hash, code)
                VALUES ($1, $2, $3)
            ''', agent_id, code_hash, code)

    async def get_code_version(self, agent_id: str, code_hash: str) -> Optional[str]:
        async with self.pool.acquire() as conn:
            return await conn.fetchval('''
                SELECT code FROM code_versions
                WHERE agent_id = $1 AND hash = $2
                ORDER BY created_at DESC
                LIMIT 1
            ''', agent_id, code_hash)
