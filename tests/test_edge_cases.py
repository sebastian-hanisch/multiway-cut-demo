"""Randfälle der Kernroutinen: k = 2, direkt verbundene Terminals, alle Standorte Terminals, Gleichstände, Grenzen inklusive (DEMO-PLAYBOOK §12)."""

import dataclasses

import pytest

import mwc_algorithm as A
import mwc_constants as C
import mwc_evaluation as ev
import mwc_scenario as S

from conftest import adj_of


def test_two_terminals_are_a_plain_minimum_cut_and_the_guarantee_is_one():
    for seed in range(1, 15):
        inst = S.make_instance("random", 10, 3.0, 2, seed)
        T = S.pick_terminals(inst, 2, seed)
        ap, ex = A.multiway_approx(inst.adj, T), A.multiway_exact(inst.adj, T)
        assert ap.cost == ex.value and A.guarantee(2) == 1.0 and ap.lower_bound <= ex.value
        assert ap.cuts[0].value == ap.cuts[1].value == ex.value                                 # beide isolierenden Schnitte sind der kleinste s-t-Schnitt


def test_directly_connected_terminals_pay_their_edge():
    adj = adj_of(2, [(0, 1)])
    ap = A.multiway_approx(adj, (0, 1))
    assert ap.cost == 1 and ap.edges == ((0, 1),) and ap.cuts[0].value == 1 and A.multiway_exact(adj, (0, 1)).value == 1
    tri = adj_of(3, [(0, 1), (1, 2), (0, 2)])
    assert A.multiway_approx(tri, (0, 1)).cost == 2 and A.multiway_exact(tri, (0, 1)).value == 2             # Terminals 0 und 1 in einem Dreieck: Kante 0-1 und einer der Wege über 2


def test_all_locations_are_terminals():
    tri = adj_of(3, [(0, 1), (1, 2), (0, 2)])
    ap, ex = A.multiway_approx(tri, (0, 1, 2)), A.multiway_exact(tri, (0, 1, 2))
    assert ex.total == 1 and ex.value == 3 and ex.count == 1 and ap.cost == 3 and ap.lower_bound == 3 and ex.labels == (0, 1, 2)
    assert ex.edges == ((0, 1), (0, 2), (1, 2))


def test_terminals_in_different_components_cost_nothing():
    adj = adj_of(4, [(0, 1), (2, 3)])
    ap = A.multiway_approx(adj, (0, 2))
    assert ap.cost == 0 and ap.edges == () and A.multiway_exact(adj, (0, 2)).value == 0 and A.separates(adj, (0, 2), ())


def test_a_unit_capacity_bundle_to_the_sink_adds_up():
    adj = adj_of(5, [(0, 1), (1, 2), (1, 3), (1, 4)])                                          # Terminal 0 am Standort 1, die drei anderen Terminals daneben
    cut = A.isolating_cut(adj, (0, 2, 3, 4), 0)
    assert cut.value == 1 and cut.edges == ((0, 1),) and cut.side == (0,)
    cut = A.isolating_cut(adj, (0, 2, 3, 4), 2)
    assert cut.value == 1 and cut.edges == ((1, 2),)


def test_greedy_k_cut_for_k_two_is_the_minimum_cut_and_k_equal_n_removes_everything():
    adj = adj_of(6, [(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)])
    g = A.kcut_greedy(adj, 2)
    assert g.cost == 1 and len(g.steps) == 1 and A.kcut_exact(adj, 2).value == 1
    path = adj_of(4, [(0, 1), (1, 2), (2, 3)])
    full = A.kcut_greedy(path, 4)
    assert full.cost == 3 and len(full.parts) == 4 and A.kcut_exact(path, 4).value == 3 and A.kcut_exact(path, 4).total == 1


def test_greedy_k_cut_on_a_disconnected_network_splits_for_free():
    adj = adj_of(6, [(0, 1), (1, 2), (3, 4), (4, 5)])
    g = A.kcut_greedy(adj, 2)
    assert g.cost == 0 and g.parts == ((0, 1, 2), (3, 4, 5))
    assert A.kcut_greedy(adj, 3).cost == 1


def test_validate_reports_every_kind_of_problem_on_tampered_analyses():
    a = ev.analyse(ev.Settings())
    assert ev.validate(a) == []
    ap = a.approx
    assert any("nicht alle Terminals getrennt" in p for p in ev.validate(dataclasses.replace(a, approx=dataclasses.replace(ap, edges=ap.edges[:1], cost=1))))
    assert any("Kosten des Verfahrens stimmen nicht" in p for p in ev.validate(dataclasses.replace(a, approx=dataclasses.replace(ap, cost=ap.cost + 1))))
    wrong_cut = dataclasses.replace(ap.cuts[0], edges=ap.cuts[0].edges[:1])
    assert any("isolierende Schnitt" in p for p in ev.validate(dataclasses.replace(a, approx=dataclasses.replace(ap, cuts=(wrong_cut,) + ap.cuts[1:]))))
    assert any("unter der unteren Schranke" in p for p in ev.validate(dataclasses.replace(a, approx=dataclasses.replace(ap, lower_bound=ap.cost + 1))))
    ex = a.exact
    assert any("unter dem Optimum" in p for p in ev.validate(dataclasses.replace(a, exact=dataclasses.replace(ex, value=ap.cost + 1, edges=ex.edges + ap.edges[:1]))))
    assert any("über der Garantie" in p for p in ev.validate(dataclasses.replace(a, exact=dataclasses.replace(ex, value=2, edges=ex.edges[:2]))))
    assert any("untere Schranke liegt über dem Optimum" in p for p in ev.validate(dataclasses.replace(a, approx=dataclasses.replace(ap, lower_bound=ex.value + 1))))
    assert any("trennt die Terminals nicht" in p for p in ev.validate(dataclasses.replace(a, exact=dataclasses.replace(ex, edges=()))))
    kg = a.kgreedy
    assert any("keine Zerlegung in k nichtleere Teile" in p for p in ev.validate(dataclasses.replace(a, kgreedy=dataclasses.replace(kg, parts=kg.parts[:-1]))))
    assert any("Kosten des Greedy-Zerlegens" in p for p in ev.validate(dataclasses.replace(a, kgreedy=dataclasses.replace(kg, cost=kg.cost + 1))))
    ke = a.kexact
    assert any("Greedy-Zerlegen liegt unter dem Optimum" in p for p in ev.validate(dataclasses.replace(a, kexact=dataclasses.replace(ke, value=kg.cost + 1))))
    assert any("Greedy-Zerlegen liegt über der Garantie" in p for p in ev.validate(dataclasses.replace(a, kexact=dataclasses.replace(ke, value=1))))


def test_the_enumeration_limits_are_inclusive_and_the_analysis_is_deterministic():
    assert ev.analyse(ev.Settings(kind="random", n=C.BRUTE_N, seed=3)).exact is not None and ev.analyse(ev.Settings(kind="random", n=C.BRUTE_N + 1, seed=3)).exact is None
    assert ev.analyse(ev.Settings(kind="random", n=C.BRUTE_KCUT_N, seed=3)).kexact is not None and ev.analyse(ev.Settings(kind="random", n=C.BRUTE_KCUT_N + 1, seed=3)).kexact is None
    a1, a2 = ev.analyse(ev.Settings(kind="random", n=11, seed=5)), ev.analyse(ev.Settings(kind="random", n=11, seed=5))
    assert a1.approx == a2.approx and a1.exact == a2.exact and a1.kgreedy == a2.kgreedy and a1.terminals == a2.terminals


def test_the_analysis_properties():
    a = ev.analyse(ev.Settings(**C.PRESETS["Eine Lücke im Zufallsnetz"]))
    assert a.k == 4 and a.n == 12 and a.m == a.inst.m and a.cost == 9 and a.optimum == 7 and a.ratio == pytest.approx(9 / 7) and a.guarantee == 1.5 and a.lb_ratio == pytest.approx(9 / 7)
    assert a.kcost == a.kgreedy.cost and a.kopt is None
    big = ev.analyse(ev.Settings(**C.PRESETS["Großes Netz: nur die untere Schranke"]))
    assert big.optimum is None and big.ratio is None and big.lb_ratio == pytest.approx(9 / 7)


def test_size_and_k_boundaries_of_the_regler_range():
    for k in (C.K_MIN, C.K_MAX):
        for n in (C.N_MIN, C.N_MAX):
            a = ev.analyse(ev.Settings(kind="random", n=n, deg=C.DEG_MIN, links=C.LINKS_MIN, seed=1, k=k))
            assert a.n == n and a.k == k and ev.validate(a) == [], (k, n)
    a = ev.analyse(ev.Settings(kind="tight", k=C.K_MAX))
    assert a.n == 10 and a.cost == 8 and a.optimum == 5
