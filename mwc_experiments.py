"""Experimente über feste Netze (nie ein einzelner Zufalls-Seed als Befund). Jede Funktion gibt eine Liste von Zeilen (dict) zurück; Verdikte und Abbildungen lesen nur diese Zeilen.

1. `exactness_rows`: stimmen die isolierenden Schnitte, ihre Vereinigung, die untere Schranke und die Aufzählung miteinander überein (Zeugnisse, Garantie)?
2. `ratio_rows`: wie nah liegt das Verfahren am Optimum, und wann ist die Garantie erreicht?
3. `tight_rows`: der Zyklus mit abwechselnden Terminals: das Verhältnis ist genau 2 − 2/k.
4. `big_rows`: im großen Netz: Kosten gegen die untere Schranke (die Hälfte der Summe der isolierenden Schnitte).
5. `kcut_rows`: Greedy-Zerlegen gegen die Aufzählung aller Zerlegungen."""

import mwc_algorithm as A
import mwc_constants as C
import mwc_evaluation as ev
import mwc_scenario as S


def kind_label(kind, deg):
    name = C.KIND_NAMES[kind]
    return f"{name}, Grad {deg:g}".replace(".", ",") if kind in ("random", "verbund") else name


def _net(kind, deg, n, seed, k=3):
    inst = S.make_instance(kind, n, deg, 1, seed, k)
    return inst, S.pick_terminals(inst, k, seed)


def _isolating_ok(adj, terminals, approx):
    for c in approx.cuts:
        comps = A.components_without(adj, c.edges)
        mine = next(comp for comp in comps if c.terminal in comp)
        if any(t in mine for t in terminals if t != c.terminal) or c.value != len(c.edges):
            return False
    return True


def exactness_rows():
    rows = []
    for kind, deg in C.EX_KINDS:
        checks = wrong = 0
        for seed in C.SWEEP_SEEDS:
            for k in C.EX_KS:
                inst, T = _net(kind, deg, C.EX_N, seed, k)
                adj = inst.adj
                ap = A.multiway_approx(adj, T)
                ex = A.multiway_exact(adj, T)
                res = [A.separates(adj, T, ap.edges), A.separates(adj, T, ex.edges), len(ex.edges) == ex.value, ap.cost == len(set(ap.edges)), _isolating_ok(adj, T, ap),
                       ap.cost >= ex.value, ev.within_guarantee(ap.cost, ex.value, k), ap.lower_bound <= ex.value]
                checks += len(res)
                wrong += res.count(False)
        rows.append({"kind": kind, "deg": deg, "label": kind_label(kind, deg), "nets": len(C.SWEEP_SEEDS) * len(C.EX_KS), "checks": checks, "wrong": wrong, "n": C.EX_N})
    return rows


def ratio_rows():
    rows = []
    for kind, deg in C.EX_KINDS:
        for k in C.EX_KS:
            row = {"kind": kind, "deg": deg, "label": kind_label(kind, deg), "k": k, "nets": 0, "exact": 0, "sum_ratio": 0.0, "max_ratio": 1.0, "tight": 0, "sum_alg": 0, "sum_opt": 0, "n": C.EX_N}
            for seed in C.SWEEP_SEEDS:
                inst, T = _net(kind, deg, C.EX_N, seed, k)
                ap = A.multiway_approx(inst.adj, T)
                ex = A.multiway_exact(inst.adj, T)
                ratio = ap.cost / ex.value
                row["nets"] += 1
                row["exact"] += ap.cost == ex.value
                row["sum_ratio"] += ratio
                row["max_ratio"] = max(row["max_ratio"], ratio)
                row["tight"] += ap.cost * k == (2 * k - 2) * ex.value and ap.cost > ex.value
                row["sum_alg"] += ap.cost
                row["sum_opt"] += ex.value
            rows.append(row)
    return rows


def tight_rows():
    rows = []
    for k in C.TIGHT_KS:
        inst = S.make_instance("tight", 0, 0, 0, 0, k)
        T = S.pick_terminals(inst, k, 0)
        ap = A.multiway_approx(inst.adj, T)
        ex = A.multiway_exact(inst.adj, T)
        rows.append({"k": k, "n": inst.n, "alg": ap.cost, "opt": ex.value, "lb": ap.lower_bound, "iso": [c.value for c in ap.cuts], "total": ex.total, "count": ex.count})
    return rows


def big_rows():
    rows = []
    for kind, deg in C.EX_KINDS:
        for k in C.EX_KS:
            row = {"kind": kind, "deg": deg, "label": kind_label(kind, deg), "k": k, "nets": 0, "n": 0, "sum_alg": 0, "sum_lb": 0, "max_alg_lb": 1.0, "sum_kept": 0, "sum_total": 0}
            for seed in C.SWEEP_SEEDS[:C.EX_BIG_SEEDS]:
                inst, T = _net(kind, deg, C.EX_BIG_N, seed, k)
                ap = A.multiway_approx(inst.adj, T)
                row["nets"] += 1
                row["n"] = inst.n
                row["sum_alg"] += ap.cost
                row["sum_lb"] += ap.lower_bound
                row["max_alg_lb"] = max(row["max_alg_lb"], ap.cost / ap.lower_bound)
                row["sum_kept"] += ap.sum_kept
                row["sum_total"] += ap.total
            rows.append(row)
    return rows


def kcut_rows():
    rows = []
    for kind, deg in C.EX_KINDS:
        for k in C.EX_KCUT_KS:
            row = {"kind": kind, "deg": deg, "label": kind_label(kind, deg), "k": k, "nets": 0, "exact": 0, "max_ratio": 1.0, "sum_greedy": 0, "sum_opt": 0, "first_single": 0, "tight": 0, "n": 0}
            for seed in C.SWEEP_SEEDS:
                inst = S.make_instance(kind, C.EX_KCUT_N, deg, 1, seed)
                g = A.kcut_greedy(inst.adj, k)
                e = A.kcut_exact(inst.adj, k)
                row["nets"] += 1
                row["n"] = inst.n
                row["exact"] += g.cost == e.value
                row["max_ratio"] = max(row["max_ratio"], g.cost / e.value if e.value else (1.0 if g.cost == 0 else float("inf")))
                row["sum_greedy"] += g.cost
                row["tight"] += g.cost > e.value and g.cost * k == (2 * k - 2) * e.value
                row["sum_opt"] += e.value
                first = g.steps[0]
                row["first_single"] += min(len(first.side), len(first.rest)) == 1
            rows.append(row)
    return rows
