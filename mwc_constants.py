"""Konstanten: Regler-Grenzen, feste Annahmen, Experiment-Raster, Farben und Presets."""

KINDS = ("tight", "random", "grid", "ring", "scalefree", "verbund", "geometric")
KIND_NAMES = {"tight": "Lehrbeispiel (Zyklus mit abwechselnden Terminals)", "random": "Zufallsnetz", "grid": "Gitter", "ring": "Ring mit Abkürzungen", "scalefree": "Skalenfreies Netz", "verbund": "Verbundnetz",
              "geometric": "Kartennetz"}
KIND_HELP = {
    "tight": "2k Standorte auf einem Kreis, jeder zweite ein Terminal: der Fall, an dem die Garantie des Verfahrens scharf ist.",
    "random": "Zufallsbaum plus zufällige Leitungen; der mittlere Grad ist einstellbar.",
    "grid": "Standorte auf einem Raster, Verbindungen zu den vier Nachbarn.",
    "ring": "Vier nächste Nachbarn auf einem Ring, ein Zehntel der Leitungen führt zu einem zufälligen Standort.",
    "scalefree": "Neue Standorte hängen sich bevorzugt an gut vernetzte an (je zwei Leitungen).",
    "verbund": "Drei Regionen mit dichten inneren Verbindungen und wenigen Leitungen dazwischen (einstellbar).",
    "geometric": "Zufällige Punkte in einem Quadrat, jeder mit seinen drei nächsten Nachbarn verbunden: ein Straßennetz im Kleinen.",
}
KIND_REGLER = {
    "tight": "Das Lehrbeispiel hat 2k Standorte: Wirksam sind nur k (Terminals) und der Aufbau fest; Standorte, Grad, Leitungen und Zufalls-Seed wirken nicht.",
    "random": "Wirksam: Standorte, mittlerer Grad, Zufalls-Seed (er legt auch die Terminals fest), Zahl der Terminals.",
    "grid": "Wirksam: Standorte (gerundet auf ein Rechteck), Zufalls-Seed (nur für die Terminals), Zahl der Terminals. Grad und Leitungen wirken nicht.",
    "ring": "Wirksam: Standorte, Zufalls-Seed, Zahl der Terminals.",
    "scalefree": "Wirksam: Standorte, Zufalls-Seed, Zahl der Terminals.",
    "verbund": "Wirksam: Standorte, mittlerer Grad (in den Regionen), Leitungen zwischen den Regionen, Zufalls-Seed, Zahl der Terminals.",
    "geometric": "Wirksam: Standorte, Zufalls-Seed, Zahl der Terminals.",
}

N_MIN, N_MAX, DEFAULT_N = 8, 80, 12
DEG_MIN, DEG_MAX, DEFAULT_DEG = 2.0, 10.0, 4.0
LINKS_MIN, LINKS_MAX, DEFAULT_LINKS = 1, 8, 2
K_MIN, K_MAX, DEFAULT_K = 2, 5, 3
SEED_MAX, DEFAULT_SEED = 999999, 7
DEFAULT_KIND = "tight"
REGIONS = 3
RING_NEIGHBOURS, RING_REWIRE = 4, 0.1
SCALEFREE_M = 2
BRUTE_N = 12                             # größte Netzgröße für die Aufzählung aller Zuordnungen beim Multiway-Cut (k^(n−k) Zuordnungen)
BRUTE_KCUT_N = 10                        # größte Netzgröße für die Aufzählung aller Zerlegungen in k Teile beim k-Schnitt
TIGHT_KS = (2, 3, 4, 5, 6)               # Zyklen des Experiments zur engen Instanz

SWEEP_SEEDS = tuple(range(100000, 100012))   # feste Netze für alle Experimente: nie ein einzelner Zufalls-Seed als Befund
EX_N = 12
EX_KS = (3, 4)
EX_KINDS = (("random", 3.0), ("random", 5.0), ("grid", 0.0), ("ring", 0.0), ("scalefree", 0.0), ("verbund", 5.0), ("geometric", 0.0))
EX_BIG_N = 64                            # Quadratzahl: das Gitter hat dieselbe Größe wie die anderen Netztypen
EX_BIG_SEEDS = 4
EX_KCUT_N = 9                            # Quadratzahl, höchstens BRUTE_KCUT_N
EX_KCUT_KS = (3, 4)

COLOR_SIDE_A = "#2F6B65"
COLOR_SIDE_B = "#4c78a8"
COLOR_CUT = "#d1495b"
COLOR_NODE = "#c9d1d3"
COLOR_EDGE = "rgba(150,150,150,0.45)"
COLOR_BAR = "#4c78a8"
COLOR_BAR2 = "#e8a33d"
COLOR_BAR3 = "#2F6B65"
COLOR_LOCK = "#8d6cab"
# Farben der Terminals (ein Terminal je Farbe) und der Rest
COLOR_TERMINALS = ("#2F6B65", "#4c78a8", "#e8a33d", "#8d6cab", "#d1495b", "#3a8f5c")
COLOR_FREE = "#c9d1d3"

PRESETS = {
    "Lehrbeispiel (Zyklus, k = 3)": {"kind": "tight", "n": DEFAULT_N, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": DEFAULT_SEED, "k": 3},
    "Die Garantie ist scharf (k = 4)": {"kind": "tight", "n": DEFAULT_N, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": DEFAULT_SEED, "k": 4},
    "Im Modellnetz stimmt es meist": {"kind": "random", "n": 12, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": 1, "k": 3},
    "Eine Lücke im Zufallsnetz": {"kind": "random", "n": 12, "deg": 3.0, "links": DEFAULT_LINKS, "seed": 31, "k": 4},
    "Terminals im Gitter": {"kind": "grid", "n": 12, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": 15, "k": 3},
    "Verbundnetz mit vier Terminals": {"kind": "verbund", "n": 12, "deg": 5.0, "links": 1, "seed": 26, "k": 4},
    "k-Schnitt: Greedy an der Garantie": {"kind": "verbund", "n": 9, "deg": 5.0, "links": 1, "seed": 1, "k": 3},
    "Großes Netz: nur die untere Schranke": {"kind": "random", "n": 64, "deg": DEFAULT_DEG, "links": DEFAULT_LINKS, "seed": 2, "k": 4},
}
PRESET_HELP = {
    "Lehrbeispiel (Zyklus, k = 3)": "Sechs Standorte auf einem Kreis, jeder zweite ein Terminal: Das Verfahren braucht 4 Leitungen, das Optimum 3 (von Hand zu prüfen).",
    "Die Garantie ist scharf (k = 4)": "Acht Standorte, vier Terminals: 6 Leitungen gegen 4, genau das 1,5-Fache und damit die Garantie 2 − 2/k.",
    "Im Modellnetz stimmt es meist": "Ein Zufallsnetz mit zwölf Standorten und drei Terminals: Das Verfahren trifft das Optimum (5 Leitungen).",
    "Eine Lücke im Zufallsnetz": "Zufallsnetz mit vier Terminals: Das Verfahren braucht 9 Leitungen, das Optimum 7 (das 1,29-Fache, die Garantie ist 1,5).",
    "Terminals im Gitter": "Gitter mit drei Terminals: 5 Leitungen gegen 4 (das 1,25-Fache, die Garantie ist 1,33).",
    "Verbundnetz mit vier Terminals": "Verbundnetz mit vier Terminals: 10 Leitungen gegen 8 (das 1,25-Fache, die Garantie ist 1,5).",
    "k-Schnitt: Greedy an der Garantie": "Verbundnetz mit neun Standorten, k = 3: Greedy-Zerlegen kostet 4, das Optimum 3, das 1,33-Fache und damit genau die Garantie 2 − 2/k (siehe Tab k-Schnitt).",
    "Großes Netz: nur die untere Schranke": "64 Standorte, keine Aufzählung mehr: Die untere Schranke (Hälfte der Summe der isolierenden Schnitte) begrenzt das Verhältnis zum Optimum.",
}
