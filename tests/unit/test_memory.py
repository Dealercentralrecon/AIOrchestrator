from unittest import TestCase

from aiorchestrator.memory import load_context, save_context


class TestMemory(TestCase):
    def test_load_empty_context(self):
        ctx = load_context()
        self.assertEqual(ctx, {})

    def test_save_and_load(self):
        test_data = {"agents": ["security", "monitor"]}
        save_context(test_data)
        loaded = load_context()
        self.assertEqual(loaded, test_data)

    def tearDown(self):
        # Cleanup test data
        save_context({})
