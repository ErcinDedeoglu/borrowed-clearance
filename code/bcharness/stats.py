"""Wilson score interval and simple tabulation."""
import math
from collections import defaultdict


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    lo, hi = max(0.0, c - h), min(1.0, c + h)
    return (0.0 if k == 0 else lo, 1.0 if k == n else hi)


def rate(rows, key):
    k = sum(1 for r in rows if r[key]); n = len(rows)
    lo, hi = wilson(k, n)
    return {"k": k, "n": n, "rate": (k / n if n else float("nan")), "lo": lo, "hi": hi}


def group(rows, *keys):
    g = defaultdict(list)
    for r in rows:
        g[tuple(r[k] for k in keys)].append(r)
    return dict(sorted(g.items()))


def newcombe_diff(k1, n1, k2, n2):
    """Newcombe (1998) hybrid score CI for p1 - p2 (method 10), from Wilson intervals."""
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2)
    d = p1 - p2
    return (d, d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2))
