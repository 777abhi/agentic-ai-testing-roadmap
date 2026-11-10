"""Day 3: MCP server protocol conformance tests."""
import unittest
from agentlab.mcp import McpServer, PROTOCOL_VERSION


def rpc(id_, method, params=None):
    r = {"jsonrpc": "2.0", "id": id_, "method": method}
    if params is not None:
        r["params"] = params
    return r


class McpTests(unittest.TestCase):
    def setUp(self):
        self.s = McpServer()

    def init(self):
        return self.s.handle(rpc(1, "initialize", {"protocolVersion": PROTOCOL_VERSION}))

    def test_rejects_calls_before_initialize(self):
        self.assertEqual(self.s.handle(rpc(1, "tools/list"))["error"]["code"], -32002)

    def test_initialize_handshake(self):
        res = self.init()["result"]
        self.assertEqual(res["protocolVersion"], PROTOCOL_VERSION)
        self.assertIn("tools", res["capabilities"])

    def test_notification_gets_no_response(self):
        self.init()
        self.assertIsNone(self.s.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_tools_list_matches_registry(self):
        self.init()
        names = {t["name"] for t in self.s.handle(rpc(2, "tools/list"))["result"]["tools"]}
        self.assertEqual(names, {"lookup_order", "issue_refund", "escalate_to_human"})

    def test_tools_call_success(self):
        self.init()
        r = self.s.handle(rpc(3, "tools/call", {"name": "lookup_order", "arguments": {"order_id": "A100"}}))
        self.assertFalse(r["result"]["isError"])

    def test_tool_failure_is_isError_not_protocol_error(self):
        self.init()
        r = self.s.handle(rpc(4, "tools/call", {"name": "issue_refund", "arguments": {"order_id": "B200", "amount": 500}}))
        self.assertNotIn("error", r)
        self.assertTrue(r["result"]["isError"])

    def test_unknown_tool_is_protocol_error(self):
        self.init()
        self.assertEqual(self.s.handle(rpc(5, "tools/call", {"name": "nope"}))["error"]["code"], -32602)

    def test_unknown_method_and_invalid_request(self):
        self.init()
        self.assertEqual(self.s.handle(rpc(6, "resources/list"))["error"]["code"], -32601)
        self.assertEqual(self.s.handle({"id": 7})["error"]["code"], -32600)


if __name__ == "__main__":
    unittest.main()
