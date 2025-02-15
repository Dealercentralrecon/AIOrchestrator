import unittest
from aiorchestrator.agents.meta_agent import MetaAgent
from aiorchestrator.security.genesis import GenesisBlock

class TestAgentCapabilities(unittest.TestCase):
    def test_self_healing_flow(self):
        agent = MetaAgent('healing_test_agent')
        broken_code = 'def handle_message(): raise Exception("Test failure")'
        
        with self.assertRaises(SecurityError):
            agent.apply_safe_modification(broken_code)
        
        self.assertEqual(len(agent.code_versions), 0)
