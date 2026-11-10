"""Minimal MCP-style JSON-RPC 2.0 server exposing agentlab tools (initialize, tools/list, tools/call)."""
import copy
from . import tools

PROTOCOL_VERSION = "2025-06-18"


class McpServer:
    def __init__(self):
        self.orders = copy.deepcopy(tools.ORDERS)
        self.initialized = False

    def handle(self, req):
        if req.get("jsonrpc") != "2.0" or "method" not in req:
            return self._err(req.get("id"), -32600, "Invalid Request")
        rid, method, params = req.get("id"), req["method"], req.get("params") or {}
        if method == "initialize":
            self.initialized = True
            return self._ok(rid, {"protocolVersion": PROTOCOL_VERSION,
                                  "capabilities": {"tools": {}},
                                  "serverInfo": {"name": "refund-mcp", "version": "1.0.0"}})
        if method == "notifications/initialized":
            return None  # notifications get no response
        if not self.initialized:
            return self._err(rid, -32002, "Server not initialized")
        if method == "tools/list":
            return self._ok(rid, {"tools": [{"name": n, "description": s["description"], "inputSchema": s["inputSchema"]}
                                            for n, s in tools.TOOL_SPECS.items()]})
        if method == "tools/call":
            name = params.get("name")
            if name not in tools.TOOL_SPECS:
                return self._err(rid, -32602, f"Unknown tool: {name}")
            try:
                res = tools.call_tool(name, params.get("arguments", {}), self.orders)
                return self._ok(rid, {"content": [{"type": "text", "text": str(res)}], "isError": False})
            except tools.ToolError as e:  # tool failures are results, not protocol errors
                return self._ok(rid, {"content": [{"type": "text", "text": str(e)}], "isError": True})
        return self._err(rid, -32601, f"Method not found: {method}")

    @staticmethod
    def _ok(rid, result):
        return {"jsonrpc": "2.0", "id": rid, "result": result}

    @staticmethod
    def _err(rid, code, msg):
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": msg}}
