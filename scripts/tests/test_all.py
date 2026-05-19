import sys
import unittest
from .test_connection import TestConnection
from .test_memory import TestMemory
from .test_knowledge import TestKnowledge
from .test_agent import TestAgent
from .test_security import TestSecurity

def run_all():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestConnection))
    suite.addTests(loader.loadTestsFromTestCase(TestMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledge))
    suite.addTests(loader.loadTestsFromTestCase(TestAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurity))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_all())
