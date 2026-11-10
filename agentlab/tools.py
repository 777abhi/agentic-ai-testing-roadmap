"""Tool registry for the Refund Support Agent (offline, deterministic)."""
from .schema import validate

ORDERS = {
    "A100": {"customer": "alice", "total": 40.0, "status": "delivered", "refunded": False},
    "B200": {"customer": "bob", "total": 900.0, "status": "delivered", "refunded": False},
    "C300": {"customer": "carol", "total": 25.0, "status": "shipped", "refunded": False},
}
REFUND_LIMIT = 100.0

TOOL_SPECS = {
    "lookup_order": {
        "description": "Fetch an order by id.",
        "inputSchema": {"type": "object", "required": ["order_id"], "additionalProperties": False,
                        "properties": {"order_id": {"type": "string"}}},
    },
    "issue_refund": {
        "description": "Refund a delivered order up to the auto-approval limit.",
        "inputSchema": {"type": "object", "required": ["order_id", "amount"], "additionalProperties": False,
                        "properties": {"order_id": {"type": "string"},
                                       "amount": {"type": "number", "minimum": 0.01, "maximum": 100.0}}},
    },
    "escalate_to_human": {
        "description": "Hand off to a human agent.",
        "inputSchema": {"type": "object", "required": ["reason"], "additionalProperties": False,
                        "properties": {"reason": {"type": "string"}}},
    },
}


class ToolError(Exception):
    pass


def call_tool(name, args, orders=None):
    orders = ORDERS if orders is None else orders
    if name not in TOOL_SPECS:
        raise ToolError(f"unknown tool '{name}'")
    errs = validate(args, TOOL_SPECS[name]["inputSchema"])
    if errs:
        raise ToolError("; ".join(errs))
    if name == "lookup_order":
        o = orders.get(args["order_id"])
        if not o:
            raise ToolError("order not found")
        return dict(o, order_id=args["order_id"])
    if name == "issue_refund":
        o = orders.get(args["order_id"])
        if not o:
            raise ToolError("order not found")
        if o["status"] != "delivered" or o["refunded"] or args["amount"] > o["total"]:
            raise ToolError("refund not allowed")
        o["refunded"] = True
        return {"refunded": args["amount"], "order_id": args["order_id"]}
    return {"escalated": True, "reason": args["reason"]}
