# aiorchestrator/core.py
from .orchestrator import Orchestrator, orchestrator
import ast
from ..db.factory import get_db_manager

class SecurityError(Exception):
    pass

class CodeValidationError(Exception):
    pass

class HotReloadError(Exception):
    pass

class Agent:
    """Base class for AI agents"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.db = get_db_manager()
        self.model = None

    async def initialize(self):
        """Called when agent is registered"""
        await self.db.connect()

    def handle_message(self, message):
        """Override with agent-specific logic"""
        raise NotImplementedError

    def shutdown(self):
        """Cleanup resources"""
        pass

    def _validate_code_change(self, new_code):
        """Sandboxed code validation"""
        # Security checks
        forbidden_patterns = [
            'os.system', 'subprocess.run',
            'open(', 'eval(', 'exec('
        ]
        
        for pattern in forbidden_patterns:
            if pattern in new_code:
                raise SecurityError(f"Forbidden pattern detected: {pattern}")
        
        # Additional security checks
        for pattern in ['pickle', 'marshal', 'ctypes']:
            if pattern in new_code:
                raise SecurityError(f"Dangerous module: {pattern}")
        
        # AST validation
        tree = ast.parse(new_code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if alias.name in ['os', 'sys', 'subprocess']:
                        raise SecurityError(f"Forbidden import: {alias.name}")
        
        # Block dangerous AST nodes
        forbidden_nodes = {
            ast.Call: ['eval', 'exec', 'open'],
            ast.Attribute: ['system', 'popen']
        }
        
        for node in ast.walk(tree):
            if isinstance(node, tuple(forbidden_nodes.keys())):
                for forbidden in forbidden_nodes[type(node)]:
                    if forbidden in ast.dump(node):
                        raise SecurityError(f'Forbidden operation: {forbidden}')

        # Syntax check
        try:
            ast.parse(new_code)
        except SyntaxError as e:
            raise CodeValidationError(f"Invalid syntax: {str(e)}")
        
        return True

    async def hot_reload(self, new_code):
        original = self._get_current_code()
        try:
            await self._write_temp_version(new_code)
            await self._run_sanity_tests()
            await self._activate_new_version()
        except Exception as e:
            await self._restore_version(original)
            raise HotReloadError(f"Rollback completed: {str(e)}")

    def _get_current_code(self):
        import inspect
        return inspect.getsource(self.__class__)

    async def _write_temp_version(self, new_code):
        from filelock import FileLock
        with FileLock(self.code_path + '.lock'):
            with open(self.code_path, 'w') as f:
                f.write(new_code)

    async def _run_sanity_tests(self):
        import subprocess
        result = subprocess.run(['pytest', '-k', self.agent_id], check=False)
        if result.returncode != 0:
            raise RuntimeError("Sanity tests failed")

    async def _activate_new_version(self):
        import importlib
        import sys
        module = sys.modules[self.__class__.__module__]
        importlib.reload(module)
        self.__class__ = getattr(module, self.__class__.__name__)

    async def _restore_version(self, original):
        with open(self.code_path, 'w') as f:
            f.write(original)

    async def _store_version(self, code: str):
        code_hash = self._generate_hash(code)
        await self.db.store_code_version(self.agent_id, code_hash, code)
        return code_hash

    def _generate_hash(self, code: str):
        # TO DO: implement hash generation
        pass


class Orchestrator:
    def __init__(self):
        self.agents = {}

    def register_agent(self, agent):
        self.agents[agent.agent_id] = agent
        agent.initialize()

    def execute_workflow(self, workflow):
        # Existing workflow logic
        pass


def initialize():
    """Initialize core services"""
    orchestrator.initialize()
    return True
