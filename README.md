# Mehrere Terminals trennen: Multiway-Cut und k-Schnitt – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-multiway-cut-demo.streamlit.app/)**

Drittes Stück der Reihe **Schnitte und Zusammenhang** (Arbeitstitel der Linie `schnitte-zusammenhang`) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“, Bereich Graphentheorie. Vehikel: ein **Verbindungsnetz zwischen Standorten** (Depots, Umschlagpunkte, Werke), synthetisch und mit festem Zufalls-Seed, alle Leitungen gleich, dazu **k Terminals**, die voneinander getrennt werden sollen. Die Demo fragt: **Wie viele Verbindungen kostet es, k Standorte voneinander zu trennen?** Für zwei Terminals ist das ein kleinster Schnitt (ein Fluss), ab drei Terminals ist die Aufgabe (**Multiway-Cut**) NP-schwer. Das einfachste Verfahren mit Gütegarantie trennt **jedes Terminal einzeln** vom Rest (**isolierender Schnitt**, ein Fluss) und nimmt die **Vereinigung der k − 1 billigsten**: höchstens das **(2 − 2/k)-Fache** des Optimums. Der zweite Tab zeigt das verwandte Problem ohne feste Terminals, den **k-Schnitt** (das Netz in k Teile zerlegen), mit Greedy-Zerlegen und derselben Garantie.

Nachbarn: den Fluss und den Zusammenhang zeigt `menger-demo`, den kleinsten Schnitt des ganzen Netzes `globaler-schnitt-demo` (Stoer–Wagner, hier im k-Schnitt benutzt), das Steinerbaum-Problem als weiteres NP-schweres Netzproblem mit Garantie `steiner-tree-demo`.

## Warum dieses Problem

Wer mehrere Standorte voneinander abkoppeln will (Teilnetze isolieren, Regionen trennen, Ausfälle eingrenzen), muss **alle Paare** trennen, und die Schnitte für verschiedene Paare dürfen sich Leitungen teilen: Deshalb ist die Summe der Einzelschnitte zu teuer und das Optimum schwer zu finden. Die Demo zeigt, **wie die isolierenden Schnitte arbeiten**, **dass die Garantie 2 − 2/k auf einem Zyklus mit abwechselnden Terminals scharf ist** (für jedes k von 2 bis 6 gemessen, von Hand beweisbar) und **dass sie auf Modellnetzen kaum zu spüren ist** (das Verfahren trifft das Optimum in 140 von 168 Instanzen). Auch ohne Aufzählung gibt eine **untere Schranke** (die Hälfte der Summe aller isolierenden Schnitte) ein Maß für die Güte.

## Befunde und Korrekturen gegenüber dem Plan

- **Die Vormessungszahlen gelten nicht:** „k = 3 exakt in 82 von 96, mittleres Verhältnis 1,025, schlechtester Fall 1,25; k = 4: 64 von 96, 1,047, 1,30“ stammen aus Wegwerfskripten mit anderen Netzen. Die Demo misst neu (Tabelle unten): **77 von 84** (k = 3) und **63 von 84** (k = 4) optimal, mittleres Verhältnis **1,02** und **1,04**, schlechtester Fall **1,25** und **1,29**.
- **Die enge Instanz ist gebaut, nicht gesucht:** Der Plan fand die Garantie 4/3 durch Zufallssuche (4 gegen 3 Leitungen bei neun Standorten). Die Demo nimmt stattdessen den **Zyklus mit abwechselnden Terminals**: Er ist für jedes k von Hand zu rechnen (Verfahren 2 (k − 1), Optimum k) und bringt exakt 2 − 2/k.
- **Kein ILP, dafür eine untere Schranke:** Der Plan sah die exakte Lösung über 12 Standorte per ILP vor. Gebaut ist die Aufzählung aller Zuordnungen bis 12 Standorte; darüber bleibt die **untere Schranke** (Hälfte der Summe der isolierenden Schnitte), die ohne Löser auskommt und das Verhältnis zum Optimum nach oben begrenzt.
- **Der k-Schnitt erreicht die Garantie auch:** Greedy-Zerlegen trifft im Verbundnetz mit neun Standorten und k = 3 in **8 von 12** Netzen genau 4 gegen 3 (1,33, die Garantie); das war nicht erwartet (Plan: „k = 3 in 39 von 39 exakt, schlechtester Fall 1,167“, aus Netzen ohne Verbundnetz). Insgesamt ist das Verfahren in **74 von 84** (k = 3) und **76 von 84** (k = 4) Instanzen optimal.
- **Terminals zufällig gezogen:** Die Terminals sind k verschiedene Standorte, gezogen mit demselben Zufalls-Seed wie das Netz; beim Zyklus liegen sie fest.

## Modell

Ein einfaches, **zusammenhängendes** Netz mit n Standorten (Zufallsnetz: Zufallsbaum plus Leitungen bis zum mittleren Grad; Gitter als Rechteck, Ring mit Abkürzungen, skalenfreies Netz nach bevorzugter Anbindung, Verbundnetz mit drei Regionen und einstellbar vielen Leitungen dazwischen, Kartennetz aus zufälligen Punkten) und das handgebaute **Lehrbeispiel**: ein **Zyklus mit 2k Standorten**, jeder zweite ein Terminal (t1, v1, t2, v2, ..., tk, vk). Von Hand: Der isolierende Schnitt jedes Terminals kostet 2 (seine beiden Leitungen), das Verfahren braucht also 2 (k − 1) Leitungen; ein Optimum durchtrennt in jeder der k Lücken zwischen zwei Terminals eine Leitung: **k**. Das Verhältnis ist **2 − 2/k**. Der Zufall kommt nur aus `random.Random(seed)` mit `random()` (plattformstabil). Details und Formeln: Expander „📐 Mathematische Formulierung“ in der App.

## Methodik

- **Isolierender Schnitt:** Für das Terminal t werden alle anderen Terminals zu einer **Senke** zusammengezogen (parallele Leitungen addieren ihre Kapazität), ein Fluss mit Edmonds–Karp berechnet den kleinsten Schnitt; von mehreren gleich billigen nimmt die Demo den mit der **kleinsten Seite** um t (die vom Terminal im Restnetz erreichbaren Standorte).
- **Verfahren:** Der **teuerste** der k isolierenden Schnitte entfällt (bei Gleichstand der des späteren Terminals), die **Vereinigung** der übrigen k − 1 ist das Ergebnis (Leitungen, die in zwei Schnitten liegen, zählen einmal). Zeugnis: Nach dem Entfernen sind alle Terminals getrennt.
- **Untere Schranke:** ⌈(Summe aller k isolierenden Schnitte) / 2⌉; jede Leitung eines Optimums liegt am Rand von höchstens zwei Komponenten, also ist das Optimum mindestens so groß.
- **Aufzählung (bis 12 Standorte):** Alle k^(n−k) Zuordnungen der übrigen Standorte zu den Terminals; der Schnitt einer Zuordnung ist die Menge der Leitungen zwischen verschieden zugeordneten Standorten; das Minimum ist das Optimum.
- **k-Schnitt, Greedy-Zerlegen:** Immer die Komponente teilen, deren kleinster Schnitt (Stoer–Wagner auf dem induzierten Teilnetz) am billigsten ist, bis k Komponenten da sind. **Aufzählung (bis 10 Standorte):** alle Zerlegungen in genau k nichtleere Teile (Stirling-Zahl zweiter Art, z. B. 7.770 bei 9 Standorten und k = 4).
- **Unabhängige Prüfer:** Die App prüft jedes Ergebnis vor der Anzeige (Terminals nach dem Entfernen getrennt, jeder isolierende Schnitt trennt sein Terminal von den anderen und hat den Wert seines Flusses, Kosten gleich der Zahl der Leitungen, nie unter der unteren Schranke, bei höchstens 12 Standorten nie unter dem Optimum und nie über der Garantie, Zerlegung in k nichtleere Teile mit nachgezählten Kosten).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py`; Zähler über feste Netze (je Netztyp zwölf Netze mit 12 Standorten und je drei und vier Terminals; beim k-Schnitt neun Standorte; im großen Netz vier je Typ mit 64 Standorten), nie ein einzelner Zufalls-Seed. Netztypen: Zufallsnetz mit mittlerem Grad 3 und 5, Gitter, Ring mit Abkürzungen, skalenfreies Netz, Verbundnetz (mittlerer Grad 5, eine Leitung zwischen je zwei Regionen), Kartennetz.

| Frage | Befund |
|---|---|
| Stimmen Zeugnisse, Schranken und Aufzählung überein? | Auf **168** Instanzen (sieben Netztypen, je zwölf Netze, k = 3 und 4) bestehen **1.344** Prüfungen (je Instanz 8): Die Leitungen des Verfahrens und des Optimums trennen alle Terminals, jeder isolierende Schnitt hat seinen Fluss als Wert, das Verfahren liegt nie unter dem Optimum und nie über der Garantie, die untere Schranke nie über dem Optimum. Abweichungen: **0**. |
| Wie nah liegt das Verfahren am Optimum? | Bei k = 3 trifft es in **77 von 84** Instanzen das Optimum (Zufallsnetz Grad 3 und 5, skalenfrei und Verbundnetz 12 von 12, Gitter 9, Ring 10, Kartennetz 10), das mittlere Verhältnis ist **1,02**, das schlechteste **1,25** (Gitter). Bei k = 4 in **63 von 84** (Gitter 6, Ring 7), Mittel **1,04**, schlechtestes **1,29** (Kartennetz, 9 gegen 7). Die Garantie (1,33 und 1,50) erreicht **keine** der 168 Instanzen. |
| Ist die Garantie irgendwo scharf? | Ja, auf dem **Zyklus mit abwechselnden Terminals**: Verfahren gegen Optimum **2 gegen 2** (k = 2), **4 gegen 3** (k = 3), **6 gegen 4** (k = 4), **8 gegen 5** (k = 5), **10 gegen 6** (k = 6): genau 2 − 2/k (1, 1,33, 1,5, 1,6, 1,67). Die Aufzählung zählt bei k = 3 **8 von 27** optimale Zuordnungen, bei k = 6 **64 von 46.656**. |
| Wie gut ist die untere Schranke im großen Netz? | Bei **64** Standorten (vier Netze je Typ und k, 28 Netze je k) kostet das Verfahren im Mittel (Quotient der Summen über die 28 Netze) das **1,11-Fache** (k = 3) bzw. das **1,26-Fache** (k = 4) der unteren Schranke, höchstens das **1,33-Fache** (Gitter, k = 3) bzw. **1,46-Fache** (Zufallsnetz Grad 5, k = 4); nie über der Garantie (1,33 und 1,50). Das Verhältnis zum Optimum liegt darunter, sagt aber nicht, wie nah das Verfahren am Optimum ist (kleine Stichprobe). |
| Überschneiden sich die genommenen Schnitte? | Ja, manchmal: Bei k = 4 und 64 Standorten liegen **257** Leitungen in den genommenen Schnitten (mit Doppelzählung), die Vereinigungen kosten **252** (5 Leitungen in zwei Schnitten); im Preset „Verbundnetz mit vier Terminals“ 10 statt 11. |
| Wie gut ist Greedy-Zerlegen beim k-Schnitt? | Bei neun Standorten trifft es bei k = 3 in **74 von 84** Instanzen das Optimum (im Verbundnetz nur in **4 von 12**), bei k = 4 in **76 von 84**; schlechtester Fall **1,33** (k = 3, Verbundnetz) bzw. **1,25** (k = 4, Zufallsnetz Grad 3). Im Verbundnetz bei k = 3 erreicht es die Garantie in **8 von 12** Netzen (4 gegen 3 Leitungen, Summe 44 gegen 36). |
| Wen trennt der erste Schnitt? | In **162 von 168** Instanzen trennt der erste Schnitt des Greedy-Zerlegens nur einen einzelnen Standort ab (Kartennetz in 18 von 24, sonst 24 von 24). |
| Sind die Preset-Beschreibungen belegt? | Ja, jedes Preset in `tests/test_claims.py` (z. B. Lehrbeispiel: 4 Leitungen gegen 3; „Eine Lücke im Zufallsnetz“: 9 gegen 7, das 1,29-Fache bei k = 4). |
| Ist die Rechnung korrekt? | Der Wert jedes isolierenden Schnitts gleich `networkx.minimum_cut` zu einer Senke (48 Netze, alle Terminals); der Multiway-Cut gleich der Aufzählung aller Leitungsmengen nach wachsender Größe (`networkx.connected_components`, 16 Netze); Verfahren, Garantie und untere Schranke auf 60 Netzen (Zeugnis: Terminals getrennt); der k-Schnitt gleich der Aufzählung aller Leitungsmengen (12 Netze, k = 3 und 4); kleinster Schnitt gleich `networkx.edge_connectivity`; Stirling-Zahlen gleich der Zahl aufgezählter Zerlegungen (`tests/test_oracle_multiwegschnitt.py`). |

## Ehrliche Grenzen

- **Das einfachste Verfahren.** Isolierende Schnitte haben die Garantie 2 − 2/k; Verfahren mit LP-Rundung erreichen kleinere Faktoren und sind nicht gebaut. Dass das einfache Verfahren auf Modellnetzen fast optimal ist, sagt nichts über seinen schlechtesten Fall (der Zyklus zeigt ihn). Die Garantie ist nicht nur auf dem Zyklus erreichbar: 4 gegen 3 Leitungen bei neun Standorten fand schon die Zufallssuche des Plans, und eine unabhängige Prüfung fand solche Fälle auch auf Netzen ohne Zyklus (die Schärfe hängt an der Wahl unter gleich billigen Schnitten).
- **Die Aufzählung ist klein:** Multiway-Cut bis 12 Standorte (k^(n−k) Zuordnungen), k-Schnitt bis 10 (Stirling-Zahl); die Netze der Experimente haben 12 bzw. 9 Standorte. Auf größeren Netzen gibt es nur die untere Schranke, kein Optimum.
- **Terminals zufällig gezogen.** Gezielt gewählte Terminals (z. B. weit auseinander oder in einer Region) wurden nicht gemessen; die Zahlen gelten für die Ziehung der Demo.
- **Ungewichtet, Kanten:** Alle Leitungen gleich; entfernt werden Leitungen, nicht Standorte (der Knoten-Multiway-Cut ist ein anderes Problem).
- **Nur k = 3 und 4 in den Zählungen:** Der Zyklus deckt k = 2 bis 6 ab, die Modellnetze nur k = 3 und 4; für k = 5 gibt es Presets und Regler, aber keine Zählung über feste Netze.
- **Größe:** bis 80 Standorte; Flüsse und Stoer–Wagner sind einfach in Python gerechnet.

## Tests

Das Verzeichnis `tests/` enthält zurzeit 129 Tests (Laufzeit etwa 30 Sekunden auf dem Entwicklungsrechner):

- **Kern** (`test_algorithm.py`): jede Einheit an von Hand gerechneten Mini-Netzen (Zyklus für k = 3 und 4, Stern, zwei Dreiecke, Pfad): Fluss mit kleinster Quellenseite, isolierende Schnitte, Vereinigung, Wegfall des teuersten, untere Schranke, Aufzählung der Zuordnungen (Zahl und Gestalt), Zuordnung der Standorte, Zerlegungen in Wuchsform, Greedy-Zerlegen Schritt für Schritt, Stirling-Zahlen.
- **Szenarien** (`test_scenario.py`): einfach, zusammenhängend, deterministisch für jeden Netztyp; Gitter als Rechteck; Zyklus; Terminals.
- **Orakel** (`test_oracle_multiwegschnitt.py`): networkx (Fluss, Komponenten, Kantenzusammenhang), Aufzählung aller Leitungsmengen, Garantie und untere Schranke auf 60 Netzen.
- **Randfälle** (`test_edge_cases.py`): k = 2, direkt verbundene Terminals, alle Standorte Terminals, getrennte Komponenten, jede Art von Prüffehler an verfälschten Analysen, Grenzen.
- **Zweige, Verdikte, Befunde** (`test_branches.py`, `test_verdicts.py`, `test_claims.py`): jedes Preset löst seine Beschreibung ein und jede Abbildung rendert; jedes Verdikt an handgesetzten Zeilen; jede Zahl dieses README.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum), Layout (Schnellstart oben, aktives Preset hervorgehoben), Footer, Laufzeit-Importe.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Terminals trennen, k-Schnitt, enge Instanz, fünf Experimente |
| `requirements-dev.txt` | Laufzeit plus pytest und networkx (Gegenproben) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `mwc_algorithm.py` | Kern: isolierende Schnitte, Multiway-Cut, Aufzählung, k-Schnitt (Greedy und Aufzählung) |
| `mwc_constants.py` | Regler-Grenzen, Netztypen, Raster der Experimente, Farben, Presets |
| `mwc_evaluation.py` | Analyse, Prüfung vor der Anzeige, Verdikte |
| `mwc_experiments.py` | Experimente über feste Netze |
| `mwc_layout.py` | Fester Kopf (Stylesheet) |
| `mwc_presets.py` | Permalink, Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `mwc_scenario.py` | Netze: Zyklus, Zufallsnetz, Gitter, Ring, skalenfreies Netz, Verbundnetz, Kartennetz; Wahl der Terminals |
| `mwc_visualization.py` | Plotly-Abbildungen (Karten mit Terminals und Schnitten, Experimente; Achsen gesperrt) |
| `tests/` | Mini-Netze, Orakel, Randfälle, Zweige, Verdikte, Befunde, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Rundung einer linearen Relaxation (Faktor 3/2 − 1/k), ILP für große Netze:** nur als Einordnung in der Formulierung.
- **Gewichte, Knoten-Multiway-Cut, gerichtete Netze:** siehe `globaler-schnitt-demo` und `menger-demo`.
- **Echte Netze oder Dateiimport:** die Netze sind synthetisch.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
