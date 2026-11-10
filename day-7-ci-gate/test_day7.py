"""Day 7: the gate itself must be tested - it must open on green and close on red."""
import unittest
from unittest import mock
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("gate", Path(__file__).with_name("gate.py"))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class GateTests(unittest.TestCase):
    def test_gate_opens_when_all_suites_pass(self):
        self.assertTrue(all(r["passed"] for r in gate.run_gate().values()))

    def test_gate_closes_when_a_suite_fails(self):
        fake = mock.Mock(returncode=1, stderr="FAILED (failures=1)")
        with mock.patch.object(gate.subprocess, "run", return_value=fake):
            self.assertFalse(any(r["passed"] for r in gate.run_gate().values()))


if __name__ == "__main__":
    unittest.main()
