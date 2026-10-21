"""Zweige der Hauptansicht (Nullspalte-Lehre): Jeder Weg, den die App zeigt, kommt in mindestens einem Preset oder einem festen Netz vor.

Ein Preset, das seine Beschreibung nicht einlöst, fällt in `test_claims.py` auf. Hier: die Zweige und dass jede Abbildung für jeden Zweig gebaut werden kann (kein Fehler, nichtleere Daten)."""

import mwc_algorithm as A
import mwc_constants as C
import mwc_evaluation as ev
import mwc_visualization as V

from conftest import cached


def _all():
    return {name: ev.analyse(ev.Settings(**p)) for name, p in C.PRESETS.items()}


def test_every_preset_validates_clean():
    for name, a in _all().items():
        assert ev.validate(a) == [], name


def test_every_branch_of_the_result_is_reached():
    analyses = list(_all().values())
    assert any(a.exact is None for a in analyses) and any(a.exact is not None for a in analyses)
    assert any(a.kexact is None for a in analyses) and any(a.kexact is not None for a in analyses)
    assert any(a.exact and a.cost == a.optimum for a in analyses) and any(a.exact and a.cost > a.optimum for a in analyses)
    assert any(a.exact and a.cost * a.k == (2 * a.k - 2) * a.optimum and a.cost > a.optimum for a in analyses)                  # die Garantie wird erreicht
    assert any(a.cost < a.approx.sum_kept for a in analyses) and any(a.cost == a.approx.sum_kept for a in analyses)           # Überschneidung der genommenen Schnitte
    assert any(a.kexact and a.kcost > a.kopt for a in analyses) and any(a.kexact and a.kcost == a.kopt for a in analyses)
    assert {a.k for a in analyses} == {3, 4} and {a.inst.kind for a in analyses} >= {"tight", "random", "grid", "verbund"}


def test_the_big_preset_is_the_only_one_without_the_enumeration():
    assert [name for name, a in _all().items() if a.exact is None] == ["Großes Netz: nur die untere Schranke"]


def test_every_net_kind_is_used_by_a_preset_or_is_a_known_extra():
    kinds = {p["kind"] for p in C.PRESETS.values()}
    assert kinds >= {"tight", "random", "grid", "verbund"}


def test_the_figures_build_for_every_preset():
    for name, a in _all().items():
        inst, T = a.inst, a.terminals
        assert V.build_map(inst, T).data, name
        assert V.build_map(inst, T, A.terminal_labels(inst.adj, T, a.approx.edges), a.approx.edges).data, name
        for c in a.approx.cuts:
            labels = tuple(T.index(c.terminal) if v in set(c.side) else -1 for v in range(a.n))
            assert V.build_map(inst, T, labels, c.edges).data
        if a.exact:
            assert V.build_map(inst, T, a.exact.labels, a.exact.edges).data
        for step in range(len(a.kgreedy.steps) + 1):
            parts = A.kcut_parts_after(a.kgreedy, step)
            assert V.build_parts_map(inst, parts).data
        if a.kexact:
            assert V.build_parts_map(inst, a.kexact.parts, a.kexact.edges).data


def test_the_experiment_figures_build_from_the_cached_rows():
    for fig, rows in ((V.build_exact, "exactness_rows"), (V.build_ratio, "ratio_rows"), (V.build_tight, "tight_rows"), (V.build_big, "big_rows"), (V.build_kcut_rows, "kcut_rows")):
        assert fig(cached(rows)).data
    assert V.color_of(-1) == C.COLOR_FREE and V.color_of(0) == C.COLOR_TERMINALS[0] and V.color_of(len(C.COLOR_TERMINALS)) == C.COLOR_TERMINALS[0]
