from abc import ABC, abstractmethod
from typing import Optional

class DatabaseManager(ABC):
    @abstractmethod
    async def connect(self):
        pass
    
    @abstractmethod
    async def store_code_version(self, agent_id: str, code_hash: str, code: str):
        pass

    @abstractmethod
    async def get_code_version(self, agent_id: str, code_hash: str) -> Optional[str]:
        pass
