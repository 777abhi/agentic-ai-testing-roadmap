"""Day 2: evaluate the agent's trajectory (not just its final answer) against golden cases."""
import unittest
from agentlab.agent import run_agent
from agentlab.trajectory import exact_match, in_order_match, precision_recall

GOLDEN = [
    {"id": "small-refund", "msg": "Please refund order A100", "expected": ["lookup_order", "issue_refund"]},
    {"id": "big-refund-escalates", "msg": "Refund order B200 now", "expected": ["lookup_order", "escalate_to_human"]},
    {"id": "no-order-id", "msg": "I want my money back", "expected": ["escalate_to_human"]},
    {"id": "status-only", "msg": "Where is order C300?", "expected": ["lookup_order"]},
]


class TrajectoryTests(unittest.TestCase):
    def test_golden_trajectories_exact(self):
        for case in GOLDEN:
            with self.subTest(case["id"]):
                out = run_agent(case["msg"])
                self.assertTrue(exact_match(out["trajectory"], case["expected"]), out["trajectory"])

    def test_lookup_precedes_refund(self):
        out = run_agent("Please refund order A100")
        self.assertTrue(in_order_match(out["trajectory"], ["lookup_order", "issue_refund"]))

    def test_never_refunds_above_limit(self):
        out = run_agent("Refund order B200 now")
        self.assertNotIn("issue_refund", [s["tool"] for s in out["trajectory"]])

    def test_precision_recall_scoring(self):
        out = run_agent("Please refund order A100")
        p, r = precision_recall(out["trajectory"], ["lookup_order", "issue_refund"])
        self.assertEqual((p, r), (1.0, 1.0))
        p, r = precision_recall(out["trajectory"], ["lookup_order", "issue_refund", "send_email"])
        self.assertAlmostEqual(r, 2 / 3)

    def test_metrics_detect_a_wrong_trajectory(self):
        bad = [{"tool": "issue_refund", "args": {}}, {"tool": "lookup_order", "args": {}}]
        self.assertFalse(in_order_match(bad, ["lookup_order", "issue_refund"]))


if __name__ == "__main__":
    unittest.main()
