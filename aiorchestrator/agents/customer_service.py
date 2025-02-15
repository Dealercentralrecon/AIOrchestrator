from ..core import Agent
from ..memory.sqlite_manager import SQLiteManager

class CustomerServiceAgent(Agent):
    def handle_message(self, message):
        """Process customer inquiries with context"""
        history = self.memory.retrieve_history(message['user_id'])
        response = self.model.generate(
            f"Context: {history}\nNew message: {message['content']}"
        )
        self.memory.store_interaction(
            user_id=message['user_id'],
            interaction={"input": message['content'], "output": response}
        )
        return response
