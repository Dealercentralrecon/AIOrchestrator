from aiorchestrator.security.genesis import GenesisBlock
from aiorchestrator.memory.sqlite_manager import SQLiteManager

class AgentFactory:
    def __init__(self):
        self.genesis = GenesisBlock()
        self.memory = SQLiteManager(':memory:')

    def spawn_agent(self, capabilities):
        blueprint = {
            'max_memory_mb': 512,
            'network_access': False,
            'allowed_imports': ['math'],
            'max_code_size_kb': 50
        }
        
        if not self.genesis.validate_blueprint(blueprint):
            raise ValueError("Invalid agent capabilities")
        
        agent_class = type('SpecializedAgent', (object,), {
            'handle': lambda self, req: self._handle_request(req, capabilities)
        })
        
        return agent_class()

    def _handle_request(self, request, capabilities):
        if 'sqrt' in capabilities:
            return int(request['value'] ** 0.5)
        raise ValueError("Unsupported operation")
