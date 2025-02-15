from .sqlite import SQLiteManager
from .postgres import PostgresManager
from ..config import config

def get_db_manager():
    if config.db_provider == "postgres":
        return PostgresManager(config.postgres_dsn)
    return SQLiteManager(config.sqlite_path)
