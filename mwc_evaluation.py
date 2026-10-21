"""Kennzahlen, Prüfung der Ergebnisse und Verdikte. Verdikte sind reine Funktionen (Art, Text): Zahlen kommen aus den Zeilen, nie aus dem Text.

Standorte sind in der Anzeige ab 1 nummeriert (`inst.name`), im Kern ab 0 (das Lehrbeispiel hat Namen t1, v1, ...)."""

from dataclasses import dataclass, field

import mwc_algorithm as A
import mwc_constants as C
import mwc_scenario as S


@dataclass(frozen=True)
class Settings:
    kind: str = C.DEFAULT_KIND
    n: int = C.DEFAULT_N
    deg: float = C.DEFAULT_DEG
    links: int = C.DEFAULT_LINKS
    seed: int = C.DEFAULT_SEED
    k: int = C.DEFAULT_K


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    inst: S.Instance = field(compare=False, repr=False)
    terminals: tuple = field(compare=False)
    approx: A.Approx = field(compare=False, repr=False)
    exact: A.ExactMultiway | None = field(compare=False, repr=False)       # nur bei höchstens BRUTE_N Standorten
    kgreedy: A.KCut = field(compare=False, repr=False)
    kexact: A.ExactKCut | None = field(compare=False, repr=False)          # nur bei höchstens BRUTE_KCUT_N Standorten

    @property
    def n(self):
        return self.inst.n

    @property
    def m(self):
        return self.inst.m

    @property
    def k(self):
        return len(self.terminals)

    @property
    def cost(self):
        return self.approx.cost

    @property
    def optimum(self):
        return self.exact.value if self.exact else None

    @property
    def ratio(self):
        return self.approx.cost / self.exact.value if self.exact and self.exact.value else None

    @property
    def guarantee(self):
        return A.guarantee(self.k)

    @property
    def lb_ratio(self):
        """Verhältnis des Verfahrens zur unteren Schranke: eine obere Grenze für das Verhältnis zum Optimum."""
        return self.approx.cost / self.approx.lower_bound if self.approx.lower_bound else None

    @property
    def kcost(self):
        return self.kgreedy.cost

    @property
    def kopt(self):
        return self.kexact.value if self.kexact else None


def within_guarantee(cost, opt, k):
    """cost ≤ (2 − 2/k) · opt in ganzen Zahlen: cost · k ≤ (2k − 2) · opt."""
    return cost * k <= (2 * k - 2) * opt


def analyse(settings: Settings) -> Analysis:
    inst = S.make_instance(settings.kind, settings.n, settings.deg, settings.links, settings.seed, settings.k)
    terminals = S.pick_terminals(inst, settings.k, settings.seed)
    adj = inst.adj
    approx = A.multiway_approx(adj, terminals)
    exact = A.multiway_exact(adj, terminals) if inst.n <= C.BRUTE_N else None
    kgreedy = A.kcut_greedy(adj, len(terminals))
    kexact = A.kcut_exact(adj, len(terminals)) if inst.n <= C.BRUTE_KCUT_N else None
    return Analysis(settings, inst, terminals, approx, exact, kgreedy, kexact)


def validate(a: Analysis) -> list:
    """Unabhängige Prüfung vor der Anzeige: gibt die Liste der Probleme zurück (leer = alles in Ordnung)."""
    problems = []
    adj, T = a.inst.adj, a.terminals
    ap = a.approx
    if not A.separates(adj, T, ap.edges):
        problems.append("Nach dem Entfernen der Leitungen des Verfahrens sind nicht alle Terminals getrennt")
    if ap.cost != len(set(ap.edges)):
        problems.append("Die Kosten des Verfahrens stimmen nicht mit der Zahl der Leitungen überein")
    for c in ap.cuts:
        comps = A.components_without(adj, c.edges)
        mine = next(comp for comp in comps if c.terminal in comp)
        if any(t in mine for t in T if t != c.terminal) or c.value != len(c.edges):
            problems.append(f"Der isolierende Schnitt des Terminals {a.inst.name(c.terminal)} trennt es nicht von den anderen oder hat den falschen Wert")
            break
    if ap.cost < ap.lower_bound:
        problems.append("Die Kosten des Verfahrens liegen unter der unteren Schranke")
    if a.exact is not None:
        ex = a.exact
        if not A.separates(adj, T, ex.edges) or len(ex.edges) != ex.value:
            problems.append("Der beste Schnitt der Aufzählung trennt die Terminals nicht oder hat den falschen Wert")
        if ap.cost < ex.value:
            problems.append("Das Verfahren liegt unter dem Optimum der Aufzählung")
        elif not within_guarantee(ap.cost, ex.value, a.k):
            problems.append("Das Verfahren liegt über der Garantie 2 − 2/k")
        if ap.lower_bound > ex.value:
            problems.append("Die untere Schranke liegt über dem Optimum")
    kg = a.kgreedy
    if len(kg.parts) != a.k or any(not p for p in kg.parts) or sorted(v for p in kg.parts for v in p) != list(range(a.n)):
        problems.append("Das Greedy-Zerlegen liefert keine Zerlegung in k nichtleere Teile")
    else:
        owner = {v: i for i, p in enumerate(kg.parts) for v in p}
        if kg.cost != sum(1 for u, v in A.edges_of(adj) if owner[u] != owner[v]) or kg.cost != sum(s.value for s in kg.steps):
            problems.append("Die Kosten des Greedy-Zerlegens stimmen nicht mit der Nachzählung überein")
    if a.kexact is not None:
        if kg.cost < a.kexact.value:
            problems.append("Das Greedy-Zerlegen liegt unter dem Optimum der Aufzählung")
        elif not within_guarantee(kg.cost, a.kexact.value, a.k):
            problems.append("Das Greedy-Zerlegen liegt über der Garantie 2 − 2/k")
    return problems


# --- Formate ---------------------------------------------------------------------------------------------------------------------------------------


def _i(x) -> str:
    """Ganze Zahl mit Punkt als Tausendertrenner."""
    return f"{x:,.0f}".replace(",", ".")


def _dec(x, digits=1) -> str:
    """Zahl mit Komma; ganze Werte ohne Nachkommastelle."""
    x = float(x)
    if x == int(x):
        return _i(x)
    return f"{x:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _r(x) -> str:
    """Verhältnis mit zwei Nachkommastellen (1,33), ganze Werte ohne."""
    return _dec(x, 2)


def _pct(share, digits=0) -> str:
    return _dec(round(100.0 * share, digits), digits) if digits else _i(round(100.0 * share))


def _of(k, n) -> str:
    return f"{_i(k)} von {_i(n)}"


def _leitungen(c) -> str:
    return "1 Leitung" if c == 1 else f"{_i(c)} Leitungen"


# --- Verdikte -------------------------------------------------------------------------------------------------------------------------------------


def verdict_multiway(a: Analysis):
    """Kernfrage: Was kostet das Verfahren, was das Optimum, und was sagt die Garantie."""
    names = [a.inst.name(c.terminal) for c in a.approx.cuts]
    values = ", ".join(f"Terminal {nm}: {_i(c.value)}" for nm, c in zip(names, a.approx.cuts))
    head = (f"**Bei {_i(a.n)} Standorten und {_i(a.k)} Terminals trennt das Verfahren mit {_leitungen(a.cost)}** (isolierende Schnitte {values}; der teuerste, Terminal {names[a.approx.dropped]}, entfällt; "
            f"die Vereinigung der übrigen kostet {_i(a.cost)} bei Summe {_i(a.approx.sum_kept)}).")
    if a.exact:
        if a.cost == a.optimum:
            body = f" Das Optimum der Aufzählung ist {_i(a.optimum)}: das Verfahren trifft es."
        else:
            body = f" Das Optimum der Aufzählung ist {_i(a.optimum)}: das Verfahren liegt beim {_r(a.ratio)}-Fachen (Garantie {_r(a.guarantee)})."
        body += f" Untere Schranke: {_i(a.approx.lower_bound)}."
    else:
        body = (f" Über {_i(C.BRUTE_N)} Standorten gibt es keine Aufzählung; die untere Schranke ist {_i(a.approx.lower_bound)}, also liegt das Verfahren höchstens beim {_r(a.lb_ratio)}-Fachen des Optimums "
                f"(Garantie {_r(a.guarantee)}).")
    return "info", head + body


def verdict_kcut(a: Analysis):
    kg = a.kgreedy
    sizes = sorted((len(p) for p in kg.parts), reverse=True)
    head = f"Greedy-Zerlegen in {_i(a.k)} Teile kostet {_leitungen(kg.cost)} (Teile mit {' + '.join(_i(s) for s in sizes)} Standorten)."
    if a.kexact:
        if kg.cost == a.kexact.value:
            body = f" Das Optimum der Aufzählung ist {_i(a.kexact.value)} ({_i(a.kexact.count)} von {_i(a.kexact.total)} Zerlegungen): das Verfahren trifft es."
        else:
            body = f" Das Optimum der Aufzählung ist {_i(a.kexact.value)}: das Verfahren liegt beim {_r(kg.cost / a.kexact.value)}-Fachen (Garantie {_r(a.guarantee)})."
    else:
        body = f" Über {_i(C.BRUTE_KCUT_N)} Standorten gibt es keine Aufzählung der Zerlegungen."
    return "info", head + body


def verdict_exact(rows):
    nets, checks, wrong = (sum(r[k] for r in rows) for k in ("nets", "checks", "wrong"))
    n = rows[0]["n"]
    if wrong:
        return "warning", f"Auf {_i(nets)} Instanzen weichen {_i(wrong)} von {_i(checks)} Prüfungen ab."
    return "info", (f"Auf {_i(nets)} Instanzen mit {_i(n)} Standorten ({len(rows)} Netztypen, je Netz drei und vier Terminals) bestehen {_i(checks)} Prüfungen: Die Leitungen des Verfahrens und des Optimums trennen alle "
                    f"Terminals, jeder isolierende Schnitt trennt sein Terminal von den anderen, das Verfahren liegt nie unter dem Optimum und nie über der Garantie 2 − 2/k, und die untere Schranke liegt nie über dem Optimum. "
                    f"Abweichungen: 0.")


def verdict_ratio(rows):
    out = []
    for k in sorted({r["k"] for r in rows}):
        sel = [r for r in rows if r["k"] == k]
        nets = sum(r["nets"] for r in sel)
        exact = sum(r["exact"] for r in sel)
        mean = sum(r["sum_ratio"] for r in sel) / nets
        worst = max(sel, key=lambda r: r["max_ratio"])
        out.append(f"Bei k = {_i(k)} trifft das Verfahren in {_of(exact, nets)} Instanzen das Optimum, das mittlere Verhältnis ist {_r(mean)}, das schlechteste {_r(worst['max_ratio'])} ({worst['label']}; Garantie {_r(A.guarantee(k))})")
    scharf = sum(r["tight"] for r in rows)
    total = sum(r["nets"] for r in rows)
    end = f"Die Garantie wird in {_i(scharf)} {'Instanz' if scharf == 1 else 'Instanzen'} erreicht." if scharf else f"Die Garantie erreicht keine der {_i(total)} Instanzen."
    return "info", ". ".join(out) + ". " + end


def verdict_tight(rows):
    ks = [r["k"] for r in rows]
    bad = [r for r in rows if r["alg"] * r["k"] != (2 * r["k"] - 2) * r["opt"]]
    if bad:
        return "warning", f"Beim Zyklus mit k = {_i(bad[0]['k'])} Terminals ist das Verhältnis nicht 2 − 2/k."
    parts = ", ".join(f"k = {_i(r['k'])}: {_i(r['alg'])} gegen {_i(r['opt'])} ({_r(r['alg'] / r['opt'])})" for r in rows)
    return "info", f"Auf dem Zyklus mit abwechselnden Terminals ist das Verhältnis genau 2 − 2/k: {parts}. Die Garantie ist also scharf, für jedes k von {_i(min(ks))} bis {_i(max(ks))} gemessen."


def verdict_big(rows):
    out = []
    for k in sorted({r["k"] for r in rows}):
        sel = [r for r in rows if r["k"] == k]
        nets = sum(r["nets"] for r in sel)
        worst = max(sel, key=lambda r: r["max_alg_lb"])
        mean = sum(r["sum_alg"] for r in sel) / sum(r["sum_lb"] for r in sel)
        out.append(f"k = {_i(k)}: Kosten im Mittel das {_r(mean)}-Fache der unteren Schranke (höchstens das {_r(worst['max_alg_lb'])}-Fache, {worst['label']}; Garantie {_r(A.guarantee(k))}), {_i(nets)} Netze")
    n = rows[0]["n"]
    return "info", f"Bei {_i(n)} Standorten (keine Aufzählung): " + "; ".join(out) + ". Die untere Schranke ist die Hälfte der Summe aller isolierenden Schnitte; das Verhältnis zum Optimum liegt darunter."


def verdict_kcut_rows(rows):
    out = []
    for k in sorted({r["k"] for r in rows}):
        sel = [r for r in rows if r["k"] == k]
        nets = sum(r["nets"] for r in sel)
        exact = sum(r["exact"] for r in sel)
        worst = max(sel, key=lambda r: r["max_ratio"])
        out.append(f"k = {_i(k)}: in {_of(exact, nets)} Instanzen optimal, schlechtestes Verhältnis {_r(worst['max_ratio'])} ({worst['label']}; Garantie {_r(A.guarantee(k))})")
    first = sum(r["first_single"] for r in rows)
    total = sum(r["nets"] for r in rows)
    scharf = sum(r["tight"] for r in rows)
    end = f" Die Garantie wird in {_of(scharf, total)} Instanzen erreicht." if scharf else ""
    return "info", (f"Greedy-Zerlegen gegen die Aufzählung aller Zerlegungen bei {_i(rows[0]['n'])} Standorten: " + "; ".join(out) + f". Der erste Schnitt trennt in {_of(first, total)} Instanzen nur einen einzelnen Standort ab." + end)
