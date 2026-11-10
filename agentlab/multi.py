"""Two-agent system: a Router that hands off to a Refund specialist. Records a handoff trace."""
from .agent import run_agent

MAX_HANDOFFS = 3


def router(user_msg):
    text = user_msg.lower()
    if "refund" in text or "money back" in text:
        return "refund_agent"
    return "info_agent"


def run_system(user_msg):
    trace, current = [], "router"
    for _ in range(MAX_HANDOFFS + 1):
        if current == "router":
            nxt = router(user_msg)
            trace.append({"from": "router", "to": nxt})
            current = nxt
            continue
        out = run_agent(user_msg)
        trace.append({"agent": current, "tools": [s["tool"] for s in out["trajectory"]]})
        return {"trace": trace, "result": out, "handoffs": sum(1 for t in trace if "to" in t)}
    raise RuntimeError("handoff loop detected")
