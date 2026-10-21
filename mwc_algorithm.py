"""Kern: Multiway-Cut durch isolierende Schnitte, die exakte Aufzählung aller Zuordnungen und der k-Schnitt durch Greedy-Zerlegen mit der exakten Aufzählung aller Zerlegungen.

**Multiway-Cut:** Gegeben ein Netz mit k Terminals; gesucht ist eine kleinste Menge von Leitungen, nach deren Entfernen keine zwei Terminals mehr verbunden sind. Für k = 2 ist das ein kleinster s-t-Schnitt (Fluss), ab
k = 3 ist die Aufgabe NP-schwer. **Isolierende Schnitte:** Für jedes Terminal t trennt ein kleinster Schnitt t von allen anderen Terminals (die anderen Terminals werden zu einer Senke zusammengezogen; Fluss,
Quellenseite so klein wie möglich). Die Vereinigung der k − 1 billigsten dieser Schnitte trennt alle Terminals und kostet höchstens (2 − 2/k)-mal so viel wie das Optimum (Dahlhaus, Johnson, Papadimitriou, Seymour,
Yannakakis 1994). Untere Schranke: Jede Leitung eines Optimums liegt in höchstens zwei isolierenden Schnitten, also ist das Optimum mindestens die Hälfte der Summe aller k isolierenden Schnitte.

**k-Schnitt:** Gesucht ist eine kleinste Menge von Leitungen, nach deren Entfernen das Netz in mindestens k Teile zerfällt. **Greedy-Zerlegen** (Saran, Vazirani 1995): Man teilt immer die Komponente, deren kleinster
Schnitt am billigsten ist, bis k Komponenten da sind; die Kosten sind höchstens (2 − 2/k)-mal das Optimum. Alle Leitungen zählen gleich (ungewichtet)."""

import math
from collections import deque
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

import mwc_constants as C


def guarantee(k):
    """Gütegarantie 2 − 2/k beider Verfahren."""
    return 2 - 2 / k


def edges_of(adj):
    return tuple((u, v) for u in range(len(adj)) for v in adj[u] if u < v)


def components_without(adj, removed, among=None):
    """Zusammenhangskomponenten (als Tupel aufsteigend, nach kleinstem Element sortiert) nach dem Entfernen der Leitungen `removed`."""
    n = len(adj)
    removed = set(removed)
    seen = [False] * n
    comps = []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        comp, queue = [s], deque([s])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if not seen[v] and (min(u, v), max(u, v)) not in removed:
                    seen[v] = True
                    comp.append(v)
                    queue.append(v)
        comps.append(tuple(sorted(comp)))
    return comps


def separates(adj, terminals, removed):
    """Sind nach dem Entfernen der Leitungen `removed` alle Terminals paarweise getrennt?"""
    comps = components_without(adj, removed)
    owner = {v: i for i, comp in enumerate(comps) for v in comp}
    return len({owner[t] for t in terminals}) == len(terminals)


# --- Isolierende Schnitte -------------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class IsolatingCut:
    terminal: int
    value: int
    side: tuple             # Quellenseite (so klein wie möglich), Standorte aufsteigend
    edges: tuple            # die Leitungen des Schnitts (u, v), u < v


def _max_flow_min_side(cap, source, sink):
    """Edmonds–Karp auf einem ungerichteten Netz mit ganzzahligen Kapazitäten (`cap`: dict von dict); gibt (Wert, von der Quelle im Restnetz erreichbare Knoten) zurück."""
    res = {u: dict(nb) for u, nb in cap.items()}
    flow = 0
    while True:
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v in sorted(res[u]):
                if res[u][v] > 0 and v not in parent:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            break
        path, v = [], sink
        while parent[v] is not None:
            path.append((parent[v], v))
            v = parent[v]
        push = min(res[u][v] for u, v in path)
        for u, v in path:
            res[u][v] -= push
            res[v][u] += push
        flow += push
    reach = {source}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in res[u]:
            if res[u][v] > 0 and v not in reach:
                reach.add(v)
                queue.append(v)
    return flow, reach


def isolating_cut(adj, terminals, t):
    """Kleinster Schnitt, der das Terminal t von allen anderen Terminals trennt (diese zu einer Senke zusammengezogen); von mehreren gleich billigen der mit der kleinsten Quellenseite."""
    n = len(adj)
    sink = n
    others = set(terminals) - {t}
    mapped = lambda v: sink if v in others else v   # noqa: E731
    cap = {v: {} for v in range(n + 1)}
    for u, v in edges_of(adj):
        a, b = mapped(u), mapped(v)
        if a == b:
            continue
        cap[a][b] = cap[a].get(b, 0) + 1
        cap[b][a] = cap[b].get(a, 0) + 1
    value, reach = _max_flow_min_side(cap, t, sink)
    side = tuple(sorted(v for v in reach if v < n))
    s = set(side)
    cut = tuple((u, v) for u, v in edges_of(adj) if (u in s) != (v in s) and not (u in others and v in others))
    return IsolatingCut(t, value, side, cut)


@dataclass(frozen=True)
class Approx:
    cuts: tuple             # die isolierenden Schnitte, in der Reihenfolge der Terminals
    dropped: int            # Index des Terminals, dessen Schnitt (der teuerste) nicht genommen wird
    edges: tuple            # Vereinigung der übrigen k − 1 Schnitte
    cost: int
    sum_kept: int           # Summe der k − 1 genommenen Werte (mit Doppelzählung)
    lower_bound: int        # ⌈ (Summe aller k Werte) / 2 ⌉

    @property
    def total(self):
        return sum(c.value for c in self.cuts)


def multiway_approx(adj, terminals):
    cuts = tuple(isolating_cut(adj, terminals, t) for t in terminals)
    order = sorted(range(len(cuts)), key=lambda i: (cuts[i].value, i))
    dropped = order[-1]
    union = sorted({e for i, c in enumerate(cuts) if i != dropped for e in c.edges})
    total = sum(c.value for c in cuts)
    return Approx(cuts, dropped, tuple(union), len(union), sum(c.value for i, c in enumerate(cuts) if i != dropped), -(-total // 2))


# --- Exakter Multiway-Cut -------------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ExactMultiway:
    value: int
    count: int              # Zahl der Zuordnungen mit diesem Wert
    labels: tuple           # eine davon (die erste): je Standort das Terminal (Index), dem er zugeordnet ist
    edges: tuple            # die Leitungen zwischen verschieden zugeordneten Standorten
    total: int              # Zahl aller Zuordnungen, k^(n − k)


def multiway_exact(adj, terminals):
    """Alle Zuordnungen der Nicht-Terminals zu den Terminals (k^(n−k)); der Schnitt einer Zuordnung ist die Menge der Leitungen zwischen verschieden zugeordneten Standorten. Das Minimum ist das Optimum."""
    n, k = len(adj), len(terminals)
    free = [v for v in range(n) if v not in set(terminals)]
    total = k ** len(free)
    idx = np.arange(total, dtype=np.int64)
    labels = np.zeros((total, n), dtype=np.int8)
    for i, t in enumerate(terminals):
        labels[:, t] = i
    for j, v in enumerate(free):
        labels[:, v] = (idx // (k ** j)) % k
    es = edges_of(adj)
    cost = np.zeros(total, dtype=np.int64)
    for u, v in es:
        cost += labels[:, u] != labels[:, v]
    best = int(cost.min())
    sel = np.flatnonzero(cost == best)
    first = tuple(int(x) for x in labels[sel[0]])
    cut = tuple((u, v) for u, v in es if first[u] != first[v])
    return ExactMultiway(best, len(sel), first, cut, total)


# --- k-Schnitt ------------------------------------------------------------------------------------------------------------------------------------


def induced_adj(adj, nodes):
    pos = {v: i for i, v in enumerate(nodes)}
    return tuple(tuple(sorted(pos[u] for u in adj[v] if u in pos)) for v in nodes)


def min_cut(adj):
    """Kleinster Schnitt ohne Balance (Stoer–Wagner, ungewichtet): (Wert, eine Seite). Bei nicht zusammenhängendem Netz ist der Wert 0."""
    n = len(adj)
    if n < 2:
        return 0, ()
    w = [[1 if v in adj[u] else 0 for v in range(n)] for u in range(n)]
    members = {v: [v] for v in range(n)}
    active = list(range(n))
    best = None
    while len(active) > 1:
        key = {v: 0 for v in active}
        rest = list(active)
        order, bind = [], []
        while rest:
            pick = min(rest, key=lambda v: (-key[v], v))
            order.append(pick)
            bind.append(key[pick])
            rest.remove(pick)
            for v in rest:
                key[v] += w[pick][v]
        last, before = order[-1], order[-2]
        if best is None or bind[-1] < best[0]:
            best = (bind[-1], tuple(sorted(members[last])))
        for x in active:
            if x != last and x != before:
                w[before][x] += w[last][x]
                w[x][before] = w[before][x]
        members[before].extend(members[last])
        active.remove(last)
    return best


@dataclass(frozen=True)
class Split:
    component: tuple        # die geteilte Komponente
    value: int              # Kosten (Leitungen innerhalb der Komponente zwischen den beiden Seiten)
    side: tuple             # die eine Seite (Standorte der Komponente)
    rest: tuple             # die andere
    candidates: tuple       # (Komponente, kleinster Schnitt) aller Komponenten dieses Schritts, in der Reihenfolge der Komponenten


@dataclass(frozen=True)
class KCut:
    k: int
    steps: tuple            # Split je Schritt
    parts: tuple            # die k Komponenten (aufsteigend nach kleinstem Element)
    cost: int
    edges: tuple            # Leitungen zwischen verschiedenen Teilen


def component_min_cut(adj, comp):
    """Kleinster Schnitt der Komponente innerhalb ihrer Leitungen: (Wert, Seite in Standorten des ganzen Netzes); None bei nur einem Standort."""
    if len(comp) < 2:
        return None
    value, side = min_cut(induced_adj(adj, comp))
    return value, tuple(sorted(comp[i] for i in side))


def kcut_greedy(adj, k):
    """Greedy-Zerlegen: Immer die Komponente teilen, deren kleinster Schnitt am billigsten ist (bei Gleichstand die erste in der Reihenfolge der Komponenten), bis es k Komponenten gibt."""
    n = len(adj)
    comps = [tuple(range(n))]
    cache = {}
    steps = []
    while len(comps) < k:
        cand = []
        for comp in comps:
            if comp not in cache:
                cache[comp] = component_min_cut(adj, comp)
            cand.append((comp, cache[comp]))
        pick = min((i for i, (_c, r) in enumerate(cand) if r is not None), key=lambda i: (cand[i][1][0], i))
        comp, (value, side) = cand[pick]
        rest = tuple(v for v in comp if v not in set(side))
        steps.append(Split(comp, value, side, rest, tuple((c, r[0] if r else None) for c, r in cand)))
        comps = [c for i, c in enumerate(comps) if i != pick] + [side, rest]
        comps.sort(key=lambda c: c[0])
    owner = {v: i for i, c in enumerate(comps) for v in c}
    cross = tuple((u, v) for u, v in edges_of(adj) if owner[u] != owner[v])
    return KCut(k, tuple(steps), tuple(comps), len(cross), cross)


@lru_cache(maxsize=None)
def partitions(n, k):
    """Alle Zerlegungen von n Standorten in genau k nichtleere Teile als Zuordnungen in aufsteigender Wuchsform (der erste Standort im Teil 0, jeder neue Teil bekommt die nächste Nummer): Feld (Zahl, n)."""
    rows = []

    def grow(prefix, used):
        pos = len(prefix)
        if pos == n:
            if used == k:
                rows.append(tuple(prefix))
            return
        if used + (n - pos) < k:
            return
        for label in range(min(used + 1, k)):
            prefix.append(label)
            grow(prefix, max(used, label + 1))
            prefix.pop()

    grow([], 0)
    return np.array(rows, dtype=np.int8)


def stirling2(n, k):
    """Stirling-Zahl zweiter Art: Zahl der Zerlegungen von n Standorten in k nichtleere Teile."""
    s = [[0] * (k + 1) for _ in range(n + 1)]
    s[0][0] = 1
    for i in range(1, n + 1):
        for j in range(1, min(i, k) + 1):
            s[i][j] = j * s[i - 1][j] + s[i - 1][j - 1]
    return s[n][k]


@dataclass(frozen=True)
class ExactKCut:
    value: int
    count: int
    parts: tuple            # eine optimale Zerlegung (die erste), als Teile in aufsteigender Reihenfolge
    edges: tuple
    total: int              # Zahl aller Zerlegungen, S(n, k)


def kcut_exact(adj, k):
    n = len(adj)
    labels = partitions(n, k)
    es = edges_of(adj)
    cost = np.zeros(len(labels), dtype=np.int64)
    for u, v in es:
        cost += labels[:, u] != labels[:, v]
    best = int(cost.min())
    sel = np.flatnonzero(cost == best)
    first = labels[sel[0]]
    parts = tuple(tuple(int(v) for v in np.flatnonzero(first == j)) for j in range(k))
    cut = tuple((u, v) for u, v in es if first[u] != first[v])
    return ExactKCut(best, len(sel), parts, cut, len(labels))


def isclose(a, b):
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def terminal_labels(adj, terminals, removed):
    """Je Standort das Terminal (Index), mit dem er nach dem Entfernen der Leitungen `removed` noch verbunden ist; -1, wenn seine Komponente kein Terminal enthält."""
    out = [-1] * len(adj)
    for comp in components_without(adj, removed):
        owners = [i for i, t in enumerate(terminals) if t in comp]
        for v in comp:
            out[v] = owners[0] if owners else -1
    return tuple(out)


def kcut_parts_after(kcut, step):
    """Die Komponenten nach den ersten `step` Teilungen des Greedy-Zerlegens (nach kleinstem Element sortiert)."""
    n = sum(len(p) for p in kcut.parts)
    comps = [tuple(range(n))]
    for s in kcut.steps[:step]:
        comps = [c for c in comps if c != s.component] + [s.side, s.rest]
        comps.sort(key=lambda c: c[0])
    return tuple(comps)
