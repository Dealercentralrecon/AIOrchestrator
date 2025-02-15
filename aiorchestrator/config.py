import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    @property
    def db_provider(self):
        return os.getenv("DB_PROVIDER", "sqlite")
    
    @property
    def sqlite_path(self):
        return os.getenv("SQLITE_PATH", "aiorchestrator.db")
    
    @property
    def postgres_dsn(self):
        return os.getenv("DATABASE_URL")

config = Config()
