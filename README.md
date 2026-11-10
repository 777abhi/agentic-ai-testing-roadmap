# Agentic AI & MCP Testing Roadmap

Reference code for the 7-day track on the QE Strategy portal. Everything is **offline and deterministic**
(Python 3.10+ standard library only): a rule-based "Refund Support Agent" stands in for an LLM so every
test is repeatable. Swap `agentlab/agent.py` for a real model call to evaluate your own agent.

| Day | Folder | Focus |
|-----|--------|-------|
| 1 | `day-1-tool-contracts` | Tool-call schema contracts, bounds, hallucinated args |
| 2 | `day-2-trajectory-eval` | Golden trajectories, in-order match, precision/recall |
| 3 | `day-3-mcp-server` | MCP JSON-RPC conformance (handshake, `isError`, error codes) |
| 4 | `day-4-red-teaming` | Indirect prompt injection and defence in depth |
| 5 | `day-5-multi-agent` | Router handoffs, loop guard, end-to-end outcome |
| 6 | `day-6-budgets` | Token / latency / step / cost budgets |
| 7 | `day-7-ci-gate` | Release gate + GitHub Actions workflow |

```bash
./run_all.sh                       # all suites
python3 day-7-ci-gate/gate.py      # gate: exit 0 = open, 1 = closed
npm run test:day4                  # single day
```
