"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds; so prüft der Test Grenzen und jede genannte Zahl direkt."""

import dataclasses

import mwc_constants as C
import mwc_evaluation as ev


def test_formats_and_the_guarantee_in_whole_numbers():
    assert ev._i(1234567) == "1.234.567" and ev._dec(3.0) == "3" and ev._dec(1234.5) == "1.234,5" and ev._dec(0.75) == "0,8" and ev._dec(2.25, 2) == "2,25"
    assert ev._r(1.0) == "1" and ev._r(4 / 3) == "1,33" and ev._r(1.5) == "1,50" and ev._pct(0.256) == "26" and ev._pct(0.256, 1) == "25,6"
    assert ev._of(3, 1200) == "3 von 1.200" and ev._leitungen(1) == "1 Leitung" and ev._leitungen(2) == "2 Leitungen" and ev._leitungen(1000) == "1.000 Leitungen"
    assert ev.within_guarantee(4, 3, 3) and not ev.within_guarantee(5, 3, 3) and ev.within_guarantee(3, 3, 3) and ev.within_guarantee(6, 4, 4) and not ev.within_guarantee(7, 4, 4)
    assert ev.within_guarantee(2, 2, 2) and not ev.within_guarantee(3, 2, 2)                      # k = 2: kein Spielraum


def test_verdict_exact_counts_and_warns_on_any_deviation():
    rows = [{"nets": 3, "checks": 30, "wrong": 0, "n": 12}, {"nets": 2, "checks": 2000, "wrong": 0, "n": 12}]
    kind, text = ev.verdict_exact(rows)
    assert kind == "info" and text.startswith("Auf 5 Instanzen mit 12 Standorten (2 Netztypen, je Netz drei und vier Terminals) bestehen 2.030 Prüfungen:") and text.endswith("Abweichungen: 0.")
    rows[1]["wrong"] = 1
    rows[0]["wrong"] = 2
    assert ev.verdict_exact(rows) == ("warning", "Auf 5 Instanzen weichen 3 von 2.030 Prüfungen ab.")


def test_verdict_ratio_per_k_and_the_guarantee_sentence():
    rows = [{"label": "A", "k": 3, "nets": 2, "exact": 1, "sum_ratio": 2.5, "max_ratio": 1.25, "tight": 0}, {"label": "B", "k": 3, "nets": 2, "exact": 2, "sum_ratio": 2.1, "max_ratio": 1.0, "tight": 0},
            {"label": "A", "k": 4, "nets": 2, "exact": 0, "sum_ratio": 3.0, "max_ratio": 1.5, "tight": 1}, {"label": "B", "k": 4, "nets": 2, "exact": 1, "sum_ratio": 2.6, "max_ratio": 1.25, "tight": 0}]
    kind, text = ev.verdict_ratio(rows)
    assert kind == "info"
    assert text == ("Bei k = 3 trifft das Verfahren in 3 von 4 Instanzen das Optimum, das mittlere Verhältnis ist 1,15, das schlechteste 1,25 (A; Garantie 1,33). Bei k = 4 trifft das Verfahren in 1 von 4 Instanzen das Optimum, "
                    "das mittlere Verhältnis ist 1,40, das schlechteste 1,50 (A; Garantie 1,50). Die Garantie wird in 1 Instanz erreicht.")
    rows[2]["tight"] = 2
    assert ev.verdict_ratio(rows)[1].endswith("Die Garantie wird in 2 Instanzen erreicht.")
    rows[2]["tight"] = 0
    assert ev.verdict_ratio(rows)[1].endswith("Die Garantie erreicht keine der 8 Instanzen.")


def test_verdict_tight_names_every_k_and_warns_when_the_ratio_is_off():
    rows = [{"k": 3, "n": 6, "alg": 4, "opt": 3}, {"k": 4, "n": 8, "alg": 6, "opt": 4}]
    kind, text = ev.verdict_tight(rows)
    assert kind == "info"
    assert text == ("Auf dem Zyklus mit abwechselnden Terminals ist das Verhältnis genau 2 − 2/k: k = 3: 4 gegen 3 (1,33), k = 4: 6 gegen 4 (1,50). Die Garantie ist also scharf, für jedes k von 3 bis 4 gemessen.")
    rows[1]["alg"] = 5
    assert ev.verdict_tight(rows) == ("warning", "Beim Zyklus mit k = 4 Terminals ist das Verhältnis nicht 2 − 2/k.")


def test_verdict_big_means_the_worst_case_and_the_guarantee():
    rows = [{"label": "A", "k": 3, "nets": 2, "n": 64, "sum_alg": 10, "sum_lb": 8, "max_alg_lb": 1.5}, {"label": "B", "k": 3, "nets": 2, "n": 64, "sum_alg": 6, "sum_lb": 6, "max_alg_lb": 1.0},
            {"label": "A", "k": 4, "nets": 2, "n": 64, "sum_alg": 12, "sum_lb": 8, "max_alg_lb": 1.5}]
    kind, text = ev.verdict_big(rows)
    assert kind == "info"
    assert text == ("Bei 64 Standorten (keine Aufzählung): k = 3: Kosten im Mittel das 1,14-Fache der unteren Schranke (höchstens das 1,50-Fache, A; Garantie 1,33), 4 Netze; k = 4: Kosten im Mittel das 1,50-Fache "
                    "der unteren Schranke (höchstens das 1,50-Fache, A; Garantie 1,50), 2 Netze. Die untere Schranke ist die Hälfte der Summe aller isolierenden Schnitte; das Verhältnis zum Optimum liegt darunter.")


def test_verdict_kcut_rows_counts_and_the_guarantee_sentence():
    rows = [{"label": "A", "k": 3, "n": 9, "nets": 2, "exact": 1, "max_ratio": 4 / 3, "first_single": 2, "tight": 1}, {"label": "B", "k": 3, "n": 9, "nets": 2, "exact": 2, "max_ratio": 1.0, "first_single": 1, "tight": 0},
            {"label": "A", "k": 4, "n": 9, "nets": 2, "exact": 2, "max_ratio": 1.0, "first_single": 2, "tight": 0}]
    kind, text = ev.verdict_kcut_rows(rows)
    assert kind == "info"
    assert text == ("Greedy-Zerlegen gegen die Aufzählung aller Zerlegungen bei 9 Standorten: k = 3: in 3 von 4 Instanzen optimal, schlechtestes Verhältnis 1,33 (A; Garantie 1,33); k = 4: in 2 von 2 Instanzen optimal, "
                    "schlechtestes Verhältnis 1 (A; Garantie 1,50). Der erste Schnitt trennt in 5 von 6 Instanzen nur einen einzelnen Standort ab. Die Garantie wird in 1 von 6 Instanzen erreicht.")
    rows[0]["tight"] = 0
    assert "Die Garantie wird" not in ev.verdict_kcut_rows(rows)[1]


def _q(name, **over):
    return ev.analyse(ev.Settings(**{**C.PRESETS[name], **over}))


def test_verdict_multiway_for_the_cycle_by_hand():
    kind, text = ev.verdict_multiway(_q("Lehrbeispiel (Zyklus, k = 3)"))
    assert kind == "info"
    assert text == ("**Bei 6 Standorten und 3 Terminals trennt das Verfahren mit 4 Leitungen** (isolierende Schnitte Terminal t1: 2, Terminal t2: 2, Terminal t3: 2; der teuerste, Terminal t3, entfällt; "
                    "die Vereinigung der übrigen kostet 4 bei Summe 4). Das Optimum der Aufzählung ist 3: das Verfahren liegt beim 1,33-Fachen (Garantie 1,33). Untere Schranke: 3.")


def test_verdict_multiway_branches():
    hit = ev.verdict_multiway(_q("Im Modellnetz stimmt es meist"))[1]
    assert "Das Optimum der Aufzählung ist 5: das Verfahren trifft es. Untere Schranke: 5." in hit and "(isolierende Schnitte Terminal 1: 2, Terminal 7: 5, Terminal 10: 3; der teuerste, Terminal 7, entfällt;" in hit
    miss = ev.verdict_multiway(_q("Eine Lücke im Zufallsnetz"))[1]
    assert "das Verfahren liegt beim 1,29-Fachen (Garantie 1,50)." in miss and "Untere Schranke: 7." in miss
    overlap = ev.verdict_multiway(_q("Verbundnetz mit vier Terminals"))[1]
    assert "die Vereinigung der übrigen kostet 10 bei Summe 11)" in overlap                    # eine Leitung liegt in zwei genommenen Schnitten
    big = ev.verdict_multiway(_q("Großes Netz: nur die untere Schranke"))[1]
    assert "Über 12 Standorten gibt es keine Aufzählung; die untere Schranke ist 7, also liegt das Verfahren höchstens beim 1,29-Fachen des Optimums (Garantie 1,50)." in big and "Optimum der Aufzählung" not in big


def test_verdict_kcut_for_the_analysis_branches():
    assert ev.verdict_kcut(_q("Lehrbeispiel (Zyklus, k = 3)"))[1] == ("Greedy-Zerlegen in 3 Teile kostet 3 Leitungen (Teile mit 4 + 1 + 1 Standorten). Das Optimum der Aufzählung ist 3 (20 von 90 Zerlegungen): "
                                                                     "das Verfahren trifft es.")
    assert ev.verdict_kcut(_q("k-Schnitt: Greedy an der Garantie"))[1] == ("Greedy-Zerlegen in 3 Teile kostet 4 Leitungen (Teile mit 7 + 1 + 1 Standorten). Das Optimum der Aufzählung ist 3: "
                                                                          "das Verfahren liegt beim 1,33-Fachen (Garantie 1,33).")
    assert "Über 10 Standorten gibt es keine Aufzählung der Zerlegungen." in ev.verdict_kcut(_q("Im Modellnetz stimmt es meist"))[1]
    a = _q("k-Schnitt: Greedy an der Garantie")
    one = dataclasses.replace(a, kgreedy=dataclasses.replace(a.kgreedy, cost=1))
    assert "kostet 1 Leitung " in ev.verdict_kcut(one)[1]
