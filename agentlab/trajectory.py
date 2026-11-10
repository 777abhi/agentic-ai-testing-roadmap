"""Trajectory scoring helpers."""


def tool_names(traj):
    return [s["tool"] for s in traj]


def exact_match(actual, expected):
    return tool_names(actual) == expected


def in_order_match(actual, expected):
    it = iter(tool_names(actual))
    return all(any(a == e for a in it) for e in expected)


def precision_recall(actual, expected):
    a, e = set(tool_names(actual)), set(expected)
    if not a or not e:
        return (1.0 if a == e else 0.0), (1.0 if a == e else 0.0)
    tp = len(a & e)
    return tp / len(a), tp / len(e)
