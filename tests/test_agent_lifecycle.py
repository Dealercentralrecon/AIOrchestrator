import unittest
from aiorchestrator.core import Orchestrator
from aiorchestrator.agents.customer_service import CustomerServiceAgent

class TestAgentLifecycle(unittest.TestCase):
    def test_agent_registration(self):
        orchestrator = Orchestrator()
        agent = CustomerServiceAgent('cs_agent_1', 'models/customer_service_v1')
        orchestrator.register_agent(agent)
        self.assertIn('cs_agent_1', orchestrator.agents)

    def test_message_handling(self):
        agent = CustomerServiceAgent('test_agent', 'models/test_model')
        test_msg = {'user_id': 'u123', 'content': "Where's my order?"}
        response = agent.handle_message(test_msg)
        self.assertIsInstance(response, str)

if __name__ == '__main__':
    unittest.main()
