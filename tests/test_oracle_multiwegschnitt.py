"""Orakel-Test multiway-cut-demo: isolierende Schnitte, Multiway-Cut, untere Schranke, Garantie, k-Schnitt und kleinster Schnitt gegen unabhängige Rechenwege (DEMO-PLAYBOOK §12).

Unabhängig: `networkx.minimum_cut` (isolierender Schnitt als Schnitt zu einer Senke mit unendlich starken Leitungen zu den anderen Terminals), `networkx.connected_components` (Zeugnisse), die Aufzählung aller
Leitungsmengen nach wachsender Größe (kleinste trennende Menge, kleinste Menge, die das Netz in k Teile zerlegt) und `networkx.edge_connectivity`. Feste Netze (Seeds)."""

import itertools

import pytest

import mwc_algorithm as A
import mwc_scenario as S

nx = pytest.importorskip("networkx")

from conftest import KMINI, MINI, adj_of  # noqa: E402


def _nets(count=40, base=3000, n=8):
    kinds = ("random", "grid", "ring", "scalefree", "verbund", "geometric")
    for k in range(count):
        kind = kinds[k % len(kinds)]
        kk = (3, 4, 2)[k % 3]
        inst = S.make_instance(kind, n + k % 3, (3.0, 4.0, 5.0)[k % 3], 1 + k % 2, base + k, kk)
        yield inst, S.pick_terminals(inst, kk, base + k)


def _graph(inst):
    g = nx.Graph()
    g.add_nodes_from(range(inst.n))
    g.add_edges_from(inst.pairs)
    return g


def _components_after(inst, removed):
    g = _graph(inst)
    g.remove_edges_from(removed)
    return [set(c) for c in nx.connected_components(g)]


def _brute_multiway(inst, terminals):
    """Kleinste Zahl entfernter Leitungen, nach der keine zwei Terminals in einer Komponente liegen: alle Leitungsmengen nach wachsender Größe."""
    for r in range(len(inst.pairs) + 1):
        for subset in itertools.combinations(inst.pairs, r):
            comps = _components_after(inst, subset)
            if all(sum(1 for t in terminals if t in c) <= 1 for c in comps):
                return r
    raise AssertionError


def _brute_kcut(inst, k):
    for r in range(len(inst.pairs) + 1):
        for subset in itertools.combinations(inst.pairs, r):
            if len(_components_after(inst, subset)) >= k:
                return r
    raise AssertionError


def test_the_oracle_on_the_hand_computed_mini_networks():
    for name, (n, pairs, terminals, values, cost, opt, count, total) in MINI.items():
        inst = S.Instance(n, tuple(sorted(tuple(sorted(p)) for p in pairs)), None, "random")
        assert _brute_multiway(inst, terminals) == opt, name
    for name, (n, pairs, k, values, opt, count, total) in KMINI.items():
        inst = S.Instance(n, tuple(sorted(tuple(sorted(p)) for p in pairs)), None, "random")
        assert _brute_kcut(inst, k) == opt, name


def test_the_isolating_cut_value_equals_networkx_minimum_cut_to_a_sink():
    for inst, T in _nets(48):
        g = _graph(inst)
        nx.set_edge_attributes(g, 1, "capacity")
        g.add_node("sink")
        for t in T:
            g.add_edge("sink", t)                                                           # ohne Kapazität: unendlich stark
        for t in T:
            h = g.copy()
            h.remove_edges_from([("sink", t)])
            value, (side, other) = nx.minimum_cut(h, t, "sink")
            cut = A.isolating_cut(inst.adj, T, t)
            assert cut.value == value and cut.value == len(cut.edges), (inst.kind, t)


def test_exact_multiway_cut_equals_the_enumeration_of_all_edge_sets():
    for inst, T in _nets(24):
        if inst.m > 14:
            continue
        assert A.multiway_exact(inst.adj, T).value == _brute_multiway(inst, T), (inst.kind, inst.n, T)


def test_the_approximation_separates_stays_within_the_guarantee_and_above_the_lower_bound():
    for inst, T in _nets(60, 3200, 10):
        ap = A.multiway_approx(inst.adj, T)
        comps = _components_after(inst, ap.edges)
        assert all(sum(1 for t in T if t in c) <= 1 for c in comps)
        ex = A.multiway_exact(inst.adj, T)
        k = len(T)
        assert ex.value <= ap.cost and ap.cost * k <= (2 * k - 2) * ex.value and ap.lower_bound <= ex.value, (inst.kind, inst.n, T)
        assert len(ex.edges) == ex.value and all(sum(1 for t in T if t in c) <= 1 for c in _components_after(inst, ex.edges))


def test_the_components_and_separation_equal_networkx():
    for inst, T in _nets(24):
        removed = inst.pairs[::3]
        mine = {frozenset(c) for c in A.components_without(inst.adj, removed)}
        assert mine == {frozenset(c) for c in _components_after(inst, removed)}
        assert A.separates(inst.adj, T, removed) == all(sum(1 for t in T if t in c) <= 1 for c in _components_after(inst, removed))


def test_exact_k_cut_equals_the_enumeration_of_all_edge_sets_and_the_greedy_stays_within_the_guarantee():
    for inst, _T in _nets(18, 3400, 7):
        if inst.m > 12:
            continue
        for k in (3, 4):
            want = _brute_kcut(inst, k)
            e = A.kcut_exact(inst.adj, k)
            g = A.kcut_greedy(inst.adj, k)
            assert e.value == want and g.cost >= want and g.cost * k <= (2 * k - 2) * want + (0 if want else 10 ** 9), (inst.kind, inst.n, k)
            assert len(_components_after(inst, g.edges)) >= k and len(_components_after(inst, e.edges)) >= k


def test_min_cut_equals_the_edge_connectivity_and_zero_on_a_disconnected_network():
    for inst, _T in _nets(30, 3600, 10):
        assert A.min_cut(inst.adj)[0] == nx.edge_connectivity(_graph(inst))
    assert A.min_cut(adj_of(5, [(0, 1), (2, 3), (3, 4)]))[0] == 0


def test_stirling_numbers_equal_the_number_of_enumerated_partitions():
    for n in range(2, 9):
        for k in range(1, n + 1):
            assert A.stirling2(n, k) == len(A.partitions(n, k))
