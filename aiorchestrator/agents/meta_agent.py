from uuid import uuid4
from datetime import datetime
from ..core import Agent
from ..memory.sqlite_manager import SQLiteManager

class MetaAgent(Agent):
    def __init__(self, agent_id):
        super().__init__(agent_id, 'models/meta_agent_v1')
        self.child_agents = {}
        self.performance_log = SQLiteManager()

    def handle_message(self, message):
        try:
            response = super().handle_message(message)
            self._log_performance(message, success=True)
        except Exception as e:
            self._heal_agent(e)
            response = self.handle_message(message)
        
        if self._needs_optimization(message):
            child_agent = self._spawn_child_agent(message['task_type'])
            return child_agent.handle(message)
        return response

    def _heal_agent(self, error):
        healing_strategy = self.model.generate(f"Error: {error}\nCode Context: {self._get_current_state()}\nProposed fix:")
        if self._validate_healing(healing_strategy):
            self._apply_code_patch(healing_strategy)
            self.restart()

    def _spawn_child_agent(self, task_type):
        agent_blueprint = self.model.generate(f"Task: {task_type}\nRequired capabilities:\n- Memory: shared\n- Model type: specialized")
        child_agent = DynamicAgent(f"child_{uuid4()}", agent_blueprint)
        self.orchestrator.register_agent(child_agent)
        self.child_agents[child_agent.id] = {
            'created_at': datetime.now(),
            'task_profile': task_type
        }
        return child_agent
