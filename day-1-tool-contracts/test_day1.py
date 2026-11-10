"""Day 1: tool-call contract tests (schema, bounds, unknown tools, hallucinated args)."""
import unittest
from agentlab.tools import call_tool, ToolError, TOOL_SPECS
import copy
from agentlab import tools


class ToolContractTests(unittest.TestCase):
    def setUp(self):
        self.orders = copy.deepcopy(tools.ORDERS)

    def test_every_tool_declares_object_schema(self):
        for name, spec in TOOL_SPECS.items():
            self.assertEqual(spec["inputSchema"]["type"], "object", name)
            self.assertFalse(spec["inputSchema"].get("additionalProperties", True), name)

    def test_valid_lookup(self):
        self.assertEqual(call_tool("lookup_order", {"order_id": "A100"}, self.orders)["customer"], "alice")

    def test_missing_required_arg_rejected(self):
        with self.assertRaisesRegex(ToolError, "missing required 'amount'"):
            call_tool("issue_refund", {"order_id": "A100"}, self.orders)

    def test_wrong_type_rejected(self):
        with self.assertRaisesRegex(ToolError, "expected number"):
            call_tool("issue_refund", {"order_id": "A100", "amount": "40"}, self.orders)

    def test_hallucinated_argument_rejected(self):
        with self.assertRaisesRegex(ToolError, "unexpected property"):
            call_tool("lookup_order", {"order_id": "A100", "customer_id": "x"}, self.orders)

    def test_amount_bounds_enforced(self):
        with self.assertRaisesRegex(ToolError, "maximum"):
            call_tool("issue_refund", {"order_id": "B200", "amount": 900.0}, self.orders)

    def test_unknown_tool_rejected(self):
        with self.assertRaisesRegex(ToolError, "unknown tool"):
            call_tool("delete_database", {}, self.orders)

    def test_double_refund_blocked(self):
        call_tool("issue_refund", {"order_id": "A100", "amount": 40.0}, self.orders)
        with self.assertRaisesRegex(ToolError, "not allowed"):
            call_tool("issue_refund", {"order_id": "A100", "amount": 40.0}, self.orders)


if __name__ == "__main__":
    unittest.main()
