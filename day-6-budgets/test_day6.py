"""Day 6: cost, latency and step budgets as regression tests."""
import unittest
from agentlab.agent import run_agent

BUDGET = {"max_tokens": 400, "max_latency_ms": 500, "max_steps": 3}
PROMPTS = ["Please refund order A100", "Refund order B200 now", "Where is order C300?", "I want my money back"]
PRICE_PER_1K_TOKENS = 0.003


class BudgetTests(unittest.TestCase):
    def test_every_golden_prompt_within_budget(self):
        for p in PROMPTS:
            with self.subTest(p):
                o = run_agent(p)
                self.assertLessEqual(o["tokens"], BUDGET["max_tokens"])
                self.assertLessEqual(o["latency_ms"], BUDGET["max_latency_ms"])
                self.assertLessEqual(len(o["trajectory"]), BUDGET["max_steps"])

    def test_cost_per_1000_runs_under_ceiling(self):
        avg = sum(run_agent(p)["tokens"] for p in PROMPTS) / len(PROMPTS)
        cost_per_run = avg / 1000 * PRICE_PER_1K_TOKENS
        self.assertLess(cost_per_run * 1000, 1.00)  # USD per 1000 runs

    def test_budget_detects_a_runaway_agent(self):
        runaway = {"tokens": 9000, "latency_ms": 12000, "trajectory": [1] * 20}
        self.assertGreater(runaway["tokens"], BUDGET["max_tokens"])
        self.assertGreater(len(runaway["trajectory"]), BUDGET["max_steps"])


if __name__ == "__main__":
    unittest.main()
