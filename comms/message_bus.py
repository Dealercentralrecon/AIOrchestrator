import json
from queue import Queue
from typing import Any, Dict


class MessageBus:
    def __init__(self):
        self.queues: Dict[str, Queue] = {}

    def register_agent(self, agent_id: str):
        self.queues[agent_id] = Queue()

    def send_message(self, recipient: str, message: Dict[str, Any]):
        self.queues[recipient].put(json.dumps(message))

    def receive_message(self, agent_id: str) -> Dict[str, Any]:
        return json.loads(self.queues[agent_id].get())

    def route_to_agent(self, agent_id, message):
        channel = f'agent_{agent_id}'
        self.publish(channel, message)

    def register_agent_handler(self, agent_id, handler):
        channel = f'agent_{agent_id}'
        self.subscribe(channel, handler)
