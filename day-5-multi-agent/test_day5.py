"""Day 5: multi-agent handoff evaluation (routing accuracy, loop guard, end-to-end outcome)."""
import unittest
from agentlab.multi import router, run_system, MAX_HANDOFFS

ROUTING = [("Please refund A100", "refund_agent"), ("I want my money back for B200", "refund_agent"),
           ("Where is order C300?", "info_agent")]


class MultiAgentTests(unittest.TestCase):
    def test_routing_accuracy(self):
        hits = sum(router(m) == want for m, want in ROUTING)
        self.assertEqual(hits / len(ROUTING), 1.0)

    def test_handoff_trace_is_well_formed(self):
        out = run_system("Please refund A100")
        self.assertEqual(out["trace"][0], {"from": "router", "to": "refund_agent"})
        self.assertEqual(out["trace"][1]["agent"], "refund_agent")

    def test_handoffs_bounded(self):
        self.assertLessEqual(run_system("Please refund A100")["handoffs"], MAX_HANDOFFS)

    def test_end_to_end_outcome_state(self):
        out = run_system("Please refund A100")
        self.assertIn("issue_refund", out["trace"][1]["tools"])
        self.assertEqual(out["result"]["answer"], "Done.")

    def test_end_to_end_policy_still_enforced(self):
        out = run_system("Refund B200")
        self.assertNotIn("issue_refund", out["trace"][1]["tools"])


if __name__ == "__main__":
    unittest.main()
