"""Kern: jede Einheit an von Hand gerechneten Mini-Netzen (DEMO-PLAYBOOK §1b)."""

import pytest

import mwc_algorithm as A
import mwc_scenario as S

from conftest import KMINI, MINI, adj_of


def _net(name):
    n, pairs, terminals, *_ = MINI[name]
    return adj_of(n, pairs), terminals


def test_guarantee_and_stirling_numbers():
    assert A.guarantee(2) == 1.0 and A.guarantee(3) == pytest.approx(4 / 3) and A.guarantee(4) == 1.5 and A.guarantee(5) == pytest.approx(1.6)
    assert [A.stirling2(4, 2), A.stirling2(5, 3), A.stirling2(6, 3), A.stirling2(9, 3), A.stirling2(9, 4)] == [7, 25, 90, 3025, 7770] and A.stirling2(3, 3) == 1 and A.stirling2(3, 1) == 1


def test_edges_components_and_separation_by_hand():
    adj = adj_of(6, [(0, 1), (1, 2), (3, 4)])
    assert A.edges_of(adj) == ((0, 1), (1, 2), (3, 4))
    assert A.components_without(adj, ()) == [(0, 1, 2), (3, 4), (5,)]
    assert A.components_without(adj, [(1, 2)]) == [(0, 1), (2,), (3, 4), (5,)]
    assert A.separates(adj, (0, 3, 5), ()) and not A.separates(adj, (0, 2), ()) and A.separates(adj, (0, 2), [(1, 2)]) and A.separates(adj, (0, 2), [(0, 1)])
    assert not A.separates(adj, (0, 1), [(1, 2)]) and A.separates(adj, (0, 1), [(0, 1)])


def test_max_flow_with_the_smallest_source_side_by_hand():
    cap = {0: {1: 2, 2: 1}, 1: {0: 2, 3: 1}, 2: {0: 1, 3: 2}, 3: {1: 1, 2: 2}}
    flow, reach = A._max_flow_min_side(cap, 0, 3)
    assert flow == 2 and reach == {0, 1}                                                     # Engpass: 1-3 (Kapazität 1) und 0-2 (Kapazität 1); die Quellenseite ist {0, 1}
    cap = {0: {1: 1}, 1: {0: 1, 2: 1}, 2: {1: 1}}
    assert A._max_flow_min_side(cap, 0, 2) == (1, {0})                                    # Pfad: von mehreren gleich billigen Schnitten der mit der kleinsten Quellenseite


@pytest.mark.parametrize("name", list(MINI))
def test_isolating_cuts_of_every_mini_network(name):
    n, pairs, terminals, values, cost, opt, count, total = MINI[name]
    adj = adj_of(n, pairs)
    cuts = [A.isolating_cut(adj, terminals, t) for t in terminals]
    assert [c.value for c in cuts] == values
    for c in cuts:
        assert c.value == len(c.edges) and c.terminal in c.side and not any(t in c.side for t in terminals if t != c.terminal)
        comps = A.components_without(adj, c.edges)
        mine = next(comp for comp in comps if c.terminal in comp)
        assert not any(t in mine for t in terminals if t != c.terminal)


def test_isolating_cuts_of_the_cycle_by_hand():
    adj, T = _net("zyklus3")
    cut = A.isolating_cut(adj, T, 0)
    assert cut.value == 2 and cut.side == (0,) and cut.edges == ((0, 1), (0, 5))                # die kleinste Quellenseite: nur das Terminal, beide Leitungen
    assert A.isolating_cut(adj, T, 2).edges == ((1, 2), (2, 3)) and A.isolating_cut(adj, T, 4).side == (4,)


def test_isolating_cut_of_the_dumbbell_and_the_star_by_hand():
    adj, T = _net("hantel")
    assert A.isolating_cut(adj, T, 0) == A.IsolatingCut(0, 1, (0, 1, 2), ((2, 3),))
    assert A.isolating_cut(adj, T, 3) == A.IsolatingCut(3, 1, (3, 4, 5), ((2, 3),))
    adj, T = _net("stern")
    assert A.isolating_cut(adj, T, 1) == A.IsolatingCut(1, 1, (1,), ((0, 1),))
    adj = adj_of(3, [(0, 1), (1, 2), (0, 2)])
    assert A.isolating_cut(adj, (0, 1, 2), 0).edges == ((0, 1), (0, 2)) and A.isolating_cut(adj, (0, 1), 0).value == 2     # Dreieck: Senke aus zwei Terminals nimmt beide Leitungen auf


def test_an_edge_between_two_other_terminals_is_not_part_of_the_isolating_cut():
    adj = adj_of(3, [(0, 1), (1, 2), (0, 2)])
    cut = A.isolating_cut(adj, (0, 1, 2), 0)
    assert (1, 2) not in cut.edges and cut.value == 2


@pytest.mark.parametrize("name", list(MINI))
def test_the_approximation_of_every_mini_network(name):
    n, pairs, terminals, values, cost, opt, count, total = MINI[name]
    adj = adj_of(n, pairs)
    ap = A.multiway_approx(adj, terminals)
    assert [c.value for c in ap.cuts] == values and ap.cost == cost == len(ap.edges) and ap.total == sum(values)
    assert ap.lower_bound == -(-sum(values) // 2) <= opt and A.separates(adj, terminals, ap.edges)
    assert ap.sum_kept == sum(values) - values[ap.dropped]


def test_the_most_expensive_cut_is_dropped_and_ties_drop_the_last_terminal():
    adj, T = _net("zyklus3")
    assert A.multiway_approx(adj, T).dropped == 2                                                    # alle gleich teuer: der letzte entfällt
    adj = adj_of(3, [(0, 1), (1, 2)])
    ap = A.multiway_approx(adj, (0, 1, 2))
    assert [c.value for c in ap.cuts] == [1, 2, 1] and ap.dropped == 1 and ap.edges == ((0, 1), (1, 2)) and ap.cost == 2 and ap.sum_kept == 2        # das mittlere Terminal braucht zwei Leitungen: sein Schnitt entfällt
    assert ap.lower_bound == 2 and A.multiway_exact(adj, (0, 1, 2)).value == 2


def test_the_union_counts_a_shared_edge_once():
    adj = adj_of(4, [(0, 1), (1, 2), (2, 3), (0, 2)])
    ap = A.multiway_approx(adj, (0, 1, 3))
    assert ap.cost == len(ap.edges) <= ap.sum_kept and len(set(ap.edges)) == len(ap.edges)


@pytest.mark.parametrize("name", list(MINI))
def test_exact_multiway_cut_of_every_mini_network(name):
    n, pairs, terminals, values, cost, opt, count, total = MINI[name]
    adj = adj_of(n, pairs)
    ex = A.multiway_exact(adj, terminals)
    assert (ex.value, ex.count, ex.total) == (opt, count, total) and len(ex.edges) == ex.value
    assert A.separates(adj, terminals, ex.edges)
    assert all(ex.labels[t] == i for i, t in enumerate(terminals))


def test_exact_multiway_cut_labels_by_hand():
    adj, T = _net("pfad")
    ex = A.multiway_exact(adj, T)
    assert ex.labels == (0, 0, 0, 1) and ex.edges == ((2, 3),)                                          # die erste der drei optimalen Zuordnungen
    adj, T = _net("stern")
    assert A.multiway_exact(adj, T).labels == (0, 0, 1, 2) and A.multiway_exact(adj, T).edges == ((0, 2), (0, 3))


def test_terminal_labels_by_hand():
    adj, T = _net("hantel")
    assert A.terminal_labels(adj, T, ((2, 3),)) == (0, 0, 0, 1, 1, 1)
    assert A.terminal_labels(adj, T, ()) == (0, 0, 0, 0, 0, 0)                                          # ohne Schnitt gehören alle zum ersten Terminal der Komponente
    adj = adj_of(5, [(0, 1), (2, 3)])
    assert A.terminal_labels(adj, (0, 2), ()) == (0, 0, 1, 1, -1)                                       # Standort 4: Komponente ohne Terminal


def test_induced_adjacency_and_min_cut_by_hand():
    adj = adj_of(6, [(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])
    assert A.induced_adj(adj, (3, 4, 5)) == ((1, 2), (0, 2), (0, 1))
    assert A.induced_adj(adj, (0, 2, 3)) == ((1,), (0, 2), (1,))
    assert A.min_cut(adj) == (1, (0, 1, 2)) or A.min_cut(adj) == (1, (3, 4, 5))
    assert A.min_cut(adj_of(4, [(0, 1), (2, 3)]))[0] == 0 and A.min_cut(adj_of(1, [])) == (0, ())
    assert A.min_cut(adj_of(4, [(a, b) for a in range(4) for b in range(a + 1, 4)])) [0] == 3
    assert A.component_min_cut(adj, (4,)) is None and A.component_min_cut(adj, (3, 4, 5))[0] == 2 and A.component_min_cut(adj, (0, 1, 2, 3))[0] == 1


def test_partitions_enumeration_by_hand():
    p = A.partitions(4, 2)
    assert p.tolist() == [[0, 0, 0, 1], [0, 0, 1, 0], [0, 0, 1, 1], [0, 1, 0, 0], [0, 1, 0, 1], [0, 1, 1, 0], [0, 1, 1, 1]]
    assert len(A.partitions(5, 3)) == 25 and len(A.partitions(6, 3)) == 90 and len(A.partitions(3, 3)) == 1 and A.partitions(3, 3).tolist() == [[0, 1, 2]]
    assert all(len(set(row)) == 4 for row in A.partitions(6, 4).tolist()) and A.partitions(4, 2) is A.partitions(4, 2)


@pytest.mark.parametrize("name", list(KMINI))
def test_k_cut_of_every_mini_network(name):
    n, pairs, k, values, opt, count, total = KMINI[name]
    adj = adj_of(n, pairs)
    g = A.kcut_greedy(adj, k)
    assert [s.value for s in g.steps] == values and g.cost == sum(values) and len(g.parts) == k and sum(len(p) for p in g.parts) == n
    owner = {v: i for i, p in enumerate(g.parts) for v in p}
    assert g.cost == sum(1 for u, v in A.edges_of(adj) if owner[u] != owner[v]) == len(g.edges)
    e = A.kcut_exact(adj, k)
    assert e.value == opt and e.total == total and len(e.edges) == e.value and sum(len(p) for p in e.parts) == n
    if count is not None:
        assert e.count == count


def test_greedy_k_cut_on_the_triangle_ring_misses_the_optimum_by_exactly_the_guarantee():
    n, pairs, k, values, opt, _c, _t = KMINI["dreiecke9"]
    adj = adj_of(n, pairs)
    g, e = A.kcut_greedy(adj, k), A.kcut_exact(adj, k)
    assert g.cost == 4 and e.value == 3 and g.cost * k == (2 * k - 2) * e.value                      # 4/3 = 2 − 2/3
    assert sorted(e.parts) == [(0, 1, 2), (3, 4, 5), (6, 7, 8)] and e.edges == ((0, 8), (2, 3), (5, 6))
    first = g.steps[0]
    assert first.value == 2 and min(len(first.side), len(first.rest)) == 1                           # der erste Schnitt trennt einen einzelnen Standort ab


def test_greedy_split_tie_rule_and_candidates():
    adj = adj_of(5, [(0, 1), (1, 2), (2, 3), (3, 4)])
    g = A.kcut_greedy(adj, 3)
    s0, s1 = g.steps
    assert s0.component == (0, 1, 2, 3, 4) and s0.value == 1 and s0.candidates == (((0, 1, 2, 3, 4), 1),)
    assert len(s1.candidates) == 2 and {c for _comp, c in s1.candidates} == {1, None} or {c for _comp, c in s1.candidates} == {1}
    assert s1.value == 1 and set(s1.component) | set(s0.side) | set(s0.rest) == set(range(5))


def test_kcut_parts_after_replays_the_steps():
    n, pairs, k, *_ = KMINI["dreiecke9"]
    g = A.kcut_greedy(adj_of(n, pairs), k)
    assert A.kcut_parts_after(g, 0) == (tuple(range(9)),) and A.kcut_parts_after(g, len(g.steps)) == g.parts and len(A.kcut_parts_after(g, 1)) == 2
    assert A.kcut_parts_after(g, 1) == tuple(sorted([g.steps[0].side, g.steps[0].rest], key=lambda c: c[0]))


def test_tight_instance_by_hand():
    inst = S.make_instance("tight", 99, k=4)
    assert inst.n == 8 and inst.m == 8 and inst.labels == ("t1", "v1", "t2", "v2", "t3", "v3", "t4", "v4") and S.pick_terminals(inst, 4, 123) == (0, 2, 4, 6)
    ap = A.multiway_approx(inst.adj, S.pick_terminals(inst, 4, 0))
    assert ap.cost == 6 and A.multiway_exact(inst.adj, S.pick_terminals(inst, 4, 0)).value == 4
