import asyncio
from aiorchestrator.db import SQLiteManager, PostgresManager
from aiorchestrator.config import config

async def main():
    source = SQLiteManager(config.sqlite_path)
    dest = PostgresManager(config.postgres_dsn)
    
    await source.connect()
    await dest.connect()
    
    cursor = source.conn.cursor()
    cursor.execute('SELECT agent_id, hash, code FROM code_versions')
    
    for row in cursor.fetchall():
        await dest.store_code_version(row[0], row[1], row[2])
    
    print(f"Migrated {cursor.rowcount} records")

if __name__ == "__main__":
    asyncio.run(main())
