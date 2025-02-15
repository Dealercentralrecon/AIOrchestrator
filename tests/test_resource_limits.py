import unittest
from aiorchestrator.security.genesis import GenesisBlock

class TestResourceLimits(unittest.TestCase):
    def test_memory_constraints(self):
        gb = GenesisBlock()
        invalid_bp = {'safety_rules': {'max_memory_mb': 8192}}
        self.assertFalse(gb.validate_blueprint(invalid_bp))
