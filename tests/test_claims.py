"""Jede Zahl im README (Abschnitt „Befunde“) wird hier über dieselben Experimentfunktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4).

Zähler und Mittel über feste Netze (je Netztyp zwölf Netze mit 12 Standorten und je drei und vier Terminals, beim k-Schnitt neun Standorte, im großen Netz vier je Typ mit 64 Standorten), nie ein einzelner Zufalls-Seed.
Die Zahlen der Vormessung im Einzelplan stammen aus Wegwerfskripten mit anderen Netzen; maßgeblich sind diese hier."""

import pytest

import mwc_constants as C
import mwc_evaluation as ev

from conftest import cached

LABELS = ["Zufallsnetz, Grad 3", "Zufallsnetz, Grad 5", "Gitter", "Ring mit Abkürzungen", "Skalenfreies Netz", "Verbundnetz, Grad 5", "Kartennetz"]


def test_every_witness_and_bound_holds_on_every_small_instance():
    rows = cached("exactness_rows")
    assert [r["label"] for r in rows] == LABELS
    assert sum(r["nets"] for r in rows) == 168 and sum(r["checks"] for r in rows) == 1344 and sum(r["wrong"] for r in rows) == 0
    assert all(r["n"] == 12 and r["nets"] == 24 and r["checks"] == 192 for r in rows)                  # je Instanz 8 Prüfungen


def test_the_approximation_is_usually_optimal_and_never_at_the_guarantee_on_model_networks():
    rows = cached("ratio_rows")
    k3, k4 = [r for r in rows if r["k"] == 3], [r for r in rows if r["k"] == 4]
    assert [r["label"] for r in k3] == LABELS and [r["label"] for r in k4] == LABELS
    assert [r["exact"] for r in k3] == [12, 12, 9, 10, 12, 12, 10] and sum(r["exact"] for r in k3) == 77
    assert [r["exact"] for r in k4] == [9, 11, 6, 7, 11, 10, 9] and sum(r["exact"] for r in k4) == 63
    assert [round(r["max_ratio"], 2) for r in k3] == [1.0, 1.0, 1.25, 1.17, 1.0, 1.0, 1.2] and [round(r["max_ratio"], 2) for r in k4] == [1.25, 1.08, 1.17, 1.2, 1.12, 1.25, 1.29]
    assert round(sum(r["sum_ratio"] for r in k3) / 84, 2) == 1.02 and round(sum(r["sum_ratio"] for r in k4) / 84, 2) == 1.04
    assert sum(r["tight"] for r in rows) == 0 and all(r["nets"] == 12 for r in rows)
    assert [(r["sum_alg"], r["sum_opt"]) for r in k4][:2] == [(85, 81), (146, 145)]                         # Zufallsnetz Grad 3 und 5, k = 4, Summe über je zwölf Netze


def test_the_guarantee_is_tight_on_the_cycle_for_every_k():
    rows = cached("tight_rows")
    assert [r["k"] for r in rows] == [2, 3, 4, 5, 6] and [r["n"] for r in rows] == [4, 6, 8, 10, 12]
    assert [r["alg"] for r in rows] == [2, 4, 6, 8, 10] and [r["opt"] for r in rows] == [2, 3, 4, 5, 6] and [r["lb"] for r in rows] == [2, 3, 4, 5, 6]
    assert all(r["iso"] == [2] * r["k"] and r["alg"] == 2 * (r["k"] - 1) and r["opt"] == r["k"] and r["alg"] * r["k"] == (2 * r["k"] - 2) * r["opt"] for r in rows)
    assert [r["count"] for r in rows] == [4, 8, 16, 32, 64] and [r["total"] for r in rows] == [4, 27, 256, 3125, 46656]
    assert [round(r["alg"] / r["opt"], 2) for r in rows] == [1.0, 1.33, 1.5, 1.6, 1.67]


def test_in_the_large_network_the_cost_stays_under_the_guarantee_times_the_lower_bound():
    rows = cached("big_rows")
    k3, k4 = [r for r in rows if r["k"] == 3], [r for r in rows if r["k"] == 4]
    assert all(r["n"] == 64 and r["nets"] == 4 for r in rows)
    assert [r["sum_alg"] for r in k3] == [18, 34, 30, 29, 18, 19, 16] and [r["sum_lb"] for r in k3] == [17, 31, 24, 25, 17, 19, 15]
    assert [r["sum_alg"] for r in k4] == [33, 55, 43, 44, 27, 25, 25] and [r["sum_lb"] for r in k4] == [27, 44, 31, 33, 22, 24, 19]
    assert round(sum(r["sum_alg"] for r in k3) / sum(r["sum_lb"] for r in k3), 2) == 1.11 and round(sum(r["sum_alg"] for r in k4) / sum(r["sum_lb"] for r in k4), 2) == 1.26
    assert (round(max(r["max_alg_lb"] for r in k3), 2), round(max(r["max_alg_lb"] for r in k4), 2)) == (1.33, 1.46)
    assert all(r["max_alg_lb"] <= 2 - 2 / r["k"] + 1e-9 for r in rows)                                       # untere Schranke und Garantie: nie über 2 − 2/k
    assert sum(r["sum_total"] for r in k3) == 285 and sum(r["sum_kept"] for r in rows if r["k"] == 4) == 257 and sum(r["sum_alg"] for r in k4) == 252


def test_greedy_k_cut_against_the_enumeration_of_all_partitions():
    rows = cached("kcut_rows")
    k3, k4 = [r for r in rows if r["k"] == 3], [r for r in rows if r["k"] == 4]
    assert all(r["n"] == 9 and r["nets"] == 12 for r in rows)
    assert [r["exact"] for r in k3] == [12, 12, 12, 12, 12, 4, 10] and sum(r["exact"] for r in k3) == 74
    assert [r["exact"] for r in k4] == [10, 11, 12, 11, 12, 12, 8] and sum(r["exact"] for r in k4) == 76
    assert round(max(r["max_ratio"] for r in k3), 2) == 1.33 and round(max(r["max_ratio"] for r in k4), 2) == 1.25
    assert [r["tight"] for r in k3] == [0, 0, 0, 0, 0, 8, 0] and sum(r["tight"] for r in rows) == 8                # nur das Verbundnetz bei k = 3 erreicht die Garantie
    assert [r["first_single"] for r in k3] == [12, 12, 12, 12, 12, 12, 9] and sum(r["first_single"] for r in rows) == 162
    assert [(r["sum_greedy"], r["sum_opt"]) for r in k3][5] == (44, 36)


def test_the_preset_descriptions_hold():
    def a(name):
        return ev.analyse(ev.Settings(**C.PRESETS[name]))
    lehr = a("Lehrbeispiel (Zyklus, k = 3)")
    assert (lehr.n, lehr.cost, lehr.optimum, lehr.approx.lower_bound) == (6, 4, 3, 3) and (lehr.kcost, lehr.kopt) == (3, 3) and lehr.exact.count == 8
    scharf = a("Die Garantie ist scharf (k = 4)")
    assert (scharf.n, scharf.cost, scharf.optimum) == (8, 6, 4) and scharf.cost * 4 == 6 * scharf.optimum and scharf.ratio == pytest.approx(A_guarantee(4))
    modell = a("Im Modellnetz stimmt es meist")
    assert modell.n == 12 and modell.cost == modell.optimum == 5
    luecke = a("Eine Lücke im Zufallsnetz")
    assert (luecke.cost, luecke.optimum, luecke.k) == (9, 7, 4) and round(luecke.ratio, 2) == 1.29
    gitter = a("Terminals im Gitter")
    assert gitter.inst.kind == "grid" and gitter.n == 12 and (gitter.cost, gitter.optimum) == (5, 4)
    verbund = a("Verbundnetz mit vier Terminals")
    assert (verbund.cost, verbund.optimum, verbund.approx.sum_kept) == (10, 8, 11)
    kcut = a("k-Schnitt: Greedy an der Garantie")
    assert kcut.n == 9 and (kcut.kcost, kcut.kopt) == (4, 3) and kcut.kcost * 3 == 4 * kcut.kopt
    gross = a("Großes Netz: nur die untere Schranke")
    assert gross.n == 64 and gross.exact is None and gross.cost == 9 and gross.approx.lower_bound == 7 and round(gross.lb_ratio, 2) == 1.29


def A_guarantee(k):
    return 2 - 2 / k
