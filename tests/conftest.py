"""Gemeinsame Fixtures: die Mini-Netze, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b).

Teure Experimente laufen einmal je Testlauf (`lru_cache`) und werden von Claims-, Verdikt- und Mutationstests gemeinsam genutzt."""

import sys
from functools import lru_cache
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def adj_of(n, pairs):
    nb = [set() for _ in range(n)]
    for u, v in pairs:
        nb[u].add(v)
        nb[v].add(u)
    return tuple(tuple(sorted(s)) for s in nb)


# Von Hand gerechnete Mini-Netze: Name -> (n, Leitungen, Terminals, Werte der isolierenden Schnitte, Kosten des Verfahrens, Optimum, Zahl der optimalen Zuordnungen, Zahl aller Zuordnungen)
MINI = {
    "zyklus3": (6, [(v, (v + 1) % 6) for v in range(6)], (0, 2, 4), [2, 2, 2], 4, 3, 8, 27),                                   # t1 v1 t2 v2 t3 v3 auf einem Kreis
    "zyklus4": (8, [(v, (v + 1) % 8) for v in range(8)], (0, 2, 4, 6), [2, 2, 2, 2], 6, 4, 16, 256),
    "stern": (4, [(0, 1), (0, 2), (0, 3)], (1, 2, 3), [1, 1, 1], 2, 2, 3, 3),                                                 # Mitte 0, Terminals die drei Blätter
    "hantel": (6, [(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (2, 3)], (0, 3), [1, 1], 1, 1, 1, 16),                    # zwei Dreiecke, eine Brücke
    "pfad": (4, [(0, 1), (1, 2), (2, 3)], (0, 3), [1, 1], 1, 1, 3, 4),
}

# k-Schnitt: Name -> (n, Leitungen, k, Werte der Teilungen des Greedy-Zerlegens, Optimum, Zahl der optimalen Zerlegungen, Zahl aller Zerlegungen S(n, k))
KMINI = {
    "kreis6": (6, [(v, (v + 1) % 6) for v in range(6)], 3, [2, 1], 3, 20, 90),
    "dreiecke9": (9, [(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (6, 7), (6, 8), (7, 8), (2, 3), (5, 6), (8, 0)], 3, [2, 2], 3, None, 3025),
    "pfad5": (5, [(0, 1), (1, 2), (2, 3), (3, 4)], 3, [1, 1], 2, 6, 25),
}


class FixedRandom:
    """Liefert immer fast 1: Fisher–Yates lässt die Reihenfolge unverändert."""

    def random(self):
        return 0.999999


@pytest.fixture
def mini():
    return MINI


@lru_cache(maxsize=None)
def cached(name):
    """Einmal je Testlauf berechnete Experimente (Name der Funktion in mwc_experiments)."""
    import mwc_experiments as ex
    return getattr(ex, name)()
