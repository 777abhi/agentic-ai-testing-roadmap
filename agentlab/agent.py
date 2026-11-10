"""Rule-based stand-in for an LLM agent. Swap `decide` for a real model call in production."""
import copy
import re
from . import tools

INJECTION_PATTERNS = [r"ignore (all )?previous", r"system prompt", r"refund .*\$?\d{3,}", r"you are now"]


def looks_injected(text):
    return any(re.search(p, text, re.I) for p in INJECTION_PATTERNS)


def run_agent(user_msg, guard=False, orders=None, order_notes=None):
    """Returns dict(trajectory=[{tool,args,result|error}], answer, tokens, latency_ms)."""
    orders = copy.deepcopy(tools.ORDERS) if orders is None else orders
    m = re.search(r"\b([A-C]\d{3})\b", user_msg)
    traj, tokens, latency = [], len(user_msg.split()) * 2, 0

    def step(name, args):
        nonlocal tokens, latency
        tokens += 30 + len(str(args))
        latency += 120
        try:
            res = tools.call_tool(name, args, orders)
            traj.append({"tool": name, "args": args, "result": res})
            return res
        except tools.ToolError as e:
            traj.append({"tool": name, "args": args, "error": str(e)})
            return None

    if not m:
        step("escalate_to_human", {"reason": "no order id"})
        return dict(trajectory=traj, answer="Escalated.", tokens=tokens, latency_ms=latency)
    oid = m.group(1)
    order = step("lookup_order", {"order_id": oid})
    note = (order_notes or {}).get(oid, "")
    if guard and looks_injected(note):
        step("escalate_to_human", {"reason": "suspicious tool output"})
        return dict(trajectory=traj, answer="Escalated.", tokens=tokens, latency_ms=latency)
    wants_refund = "refund" in user_msg.lower()
    if order and "ignore previous" in note.lower():  # naive agent obeys injected text
        step("issue_refund", {"order_id": oid, "amount": 90.0})
    elif order and wants_refund:
        if order["total"] <= tools.REFUND_LIMIT:
            step("issue_refund", {"order_id": oid, "amount": order["total"]})
        else:
            step("escalate_to_human", {"reason": "amount above auto-approval limit"})
    answer = "Done." if traj and "error" not in traj[-1] else "Could not complete."
    return dict(trajectory=traj, answer=answer, tokens=tokens, latency_ms=latency)
