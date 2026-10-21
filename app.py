"""Mehrere Terminals trennen: Multiway-Cut und k-Schnitt - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Drittes Stück der Reihe „Schnitte und Zusammenhang“: Wie viele Verbindungen kostet es, k Standorte voneinander zu trennen? Isolierende Schnitte (Fluss aus Stück 1), ihre Vereinigung, die Garantie 2 − 2/k und ein
Zyklus, an dem sie scharf ist; dazu der k-Schnitt durch Greedy-Zerlegen (Stoer–Wagner aus Stück 2).

Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import mwc_algorithm as A
import mwc_constants as C
import mwc_evaluation as ev
import mwc_experiments as ex
from mwc_layout import dunkles_design, kopf_css
from mwc_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from mwc_visualization import (
    build_big,
    build_exact,
    build_kcut_rows,
    build_map,
    build_parts_map,
    build_ratio,
    build_tight,
)

st.set_page_config(page_title="Mehrere Terminals trennen: Multiway-Cut und k-Schnitt – Sebastian Hanisch", layout="wide")

_i, _dec, _r = ev._i, ev._dec, ev._r


def _show(verdict):
    kind, text = verdict
    {"success": st.success, "info": st.info, "warning": st.warning}[kind](text)


@st.cache_data(show_spinner=False, max_entries=8)
def _analysis(settings):
    return ev.analyse(settings)


@st.cache_data(show_spinner=False)
def _exactness():
    return ex.exactness_rows()


@st.cache_data(show_spinner=False)
def _ratio():
    return ex.ratio_rows()


@st.cache_data(show_spinner=False)
def _tight():
    return ex.tight_rows()


@st.cache_data(show_spinner=False)
def _big():
    return ex.big_rows()


@st.cache_data(show_spinner=False)
def _kcut():
    return ex.kcut_rows()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in mwc_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🔌 Mehrere Terminals trennen: Multiway-Cut und k-Schnitt")
st.markdown(
    """
**Wie viele Verbindungen kostet es, k Standorte voneinander zu trennen?** Für **zwei** Terminals ist das ein kleinster Schnitt und mit einem Fluss in Polynomialzeit lösbar (Stück 1 der Reihe). Ab **drei** Terminals ist die Aufgabe
**NP-schwer**: Man muss alle Terminals paarweise trennen, und die Schnitte für verschiedene Paare dürfen sich Leitungen teilen. Die Demo zeigt das einfachste Verfahren mit Gütegarantie: Man trennt **jedes Terminal einzeln** vom
Rest (**isolierender Schnitt**, ein Fluss) und nimmt die **k − 1 billigsten** dieser Schnitte zusammen. Sie kosten höchstens das **(2 − 2/k)-Fache** des Optimums.

Auffällig: Die Garantie ist auf einem **Zyklus** mit abwechselnden Terminals **scharf**, im Modellnetz aber kaum zu spüren; und die **untere Schranke** (die Hälfte der Summe aller isolierenden Schnitte) gibt auch ohne Aufzählung ein Maß für
die Güte. Der Tab **k-Schnitt** zeigt das verwandte Problem ohne feste Terminals: das Netz in k Teile zerlegen, mit der gleichen Garantie.

Das ist das dritte Stück der Reihe **Schnitte und Zusammenhang**; den Fluss und den Zusammenhang zeigt **menger-demo**, den kleinsten Schnitt des ganzen Netzes **globaler-schnitt-demo**, das Steinerbaum-Problem als weiteres
NP-schweres Netzproblem mit Garantie **steiner-tree-demo**. Weiter unten: die Experimente **🔬**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So trennt man mehrere Terminals", expanded=True):
    st.markdown(
        """
1. **Multiway-Cut:** Gesucht ist eine kleinste Menge von Leitungen, nach deren Entfernen keine zwei der k Terminals mehr verbunden sind.
2. **Isolierender Schnitt:** Für jedes Terminal t zieht man alle anderen Terminals zu einer **Senke** zusammen und rechnet den kleinsten Schnitt zwischen t und der Senke (ein Fluss). Von mehreren gleich billigen nimmt die Demo den mit der **kleinsten Seite** um t.
3. **Verfahren:** Man lässt den **teuersten** der k isolierenden Schnitte weg und nimmt die **Vereinigung** der übrigen k − 1. Sie trennt alle Terminals und kostet höchstens das (2 − 2/k)-Fache des Optimums.
4. **Untere Schranke:** Jede Leitung eines Optimums liegt am Rand von höchstens **zwei** Komponenten; deren Ränder sind zulässige Schnitte für je ein Terminal, also ist das Optimum mindestens die **Hälfte der Summe** aller k isolierenden Schnitte.
5. **Exakt:** Bis 12 Standorte zählt die Demo alle Zuordnungen der übrigen Standorte zu den Terminals (k^(n−k)) durch; der Schnitt einer Zuordnung ist die Menge der Leitungen zwischen verschieden zugeordneten Standorten.

| Begriff | Bedeutung |
|---|---|
| **Terminal** | ein Standort, der von allen anderen Terminals getrennt werden soll (Raute auf der Karte) |
| **Isolierender Schnitt** | kleinster Schnitt, der ein Terminal von allen anderen trennt |
| **Garantie 2 − 2/k** | höchstes Verhältnis der Kosten des Verfahrens zum Optimum: 1,33 bei k = 3, 1,5 bei k = 4 |
| **Untere Schranke** | Hälfte der Summe aller isolierenden Schnitte, aufgerundet: Das Optimum ist mindestens so groß |
| **k-Schnitt** | Das Netz durch Entfernen möglichst weniger Leitungen in k Teile zerlegen (ohne feste Terminals) |
| **Greedy-Zerlegen** | immer die Komponente mit dem billigsten kleinsten Schnitt teilen, bis k Komponenten da sind |
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Netz**")
    kind = st.selectbox("Art des Netzes", list(C.KINDS), format_func=C.KIND_NAMES.get, key="kind_select", help=C.KIND_HELP.get(st.session_state.get("kind_select", C.DEFAULT_KIND), ""))
    n = st.slider("Standorte n", *bounds("n_slider"), key="n_slider", help=f"Wie viele Standorte das Netz hat (das Gitter rundet auf ein Rechteck). Die Aufzählung beim Multiway-Cut läuft bis {C.BRUTE_N} Standorte, beim k-Schnitt bis {C.BRUTE_KCUT_N}.")
    deg = st.slider("Mittlerer Grad", *bounds("deg_slider"), key="deg_slider", step=0.5, help="Leitungen je Standort im Mittel; wirkt beim Zufallsnetz und innerhalb der Regionen des Verbundnetzes.")
    links = st.slider("Leitungen zwischen je zwei Regionen", *bounds("links_slider"), key="links_slider", help="Wirkt nur beim Verbundnetz.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Legt das Netz und die Wahl der Terminals fest.")
    st.button("🎲 Neues Netz erzeugen", width="stretch", on_click=randomize_seed)
    st.caption(C.KIND_REGLER[kind])
    st.markdown("**Terminals**")
    k = st.slider("Zahl der Terminals k", *bounds("k_slider"), key="k_slider", help="Wie viele Standorte voneinander getrennt werden; beim k-Schnitt die Zahl der Teile.")

sync_query_params({"kind_select": kind, "n_slider": int(n), "deg_slider": float(deg), "links_slider": int(links), "seed_input": int(seed), "k_slider": int(k)})

settings = ev.Settings(kind, int(n), float(deg), int(links), int(seed), int(k))
with st.spinner("Rechne die Schnitte..."):
    a = _analysis(settings)
problems = ev.validate(a)
for p in problems:
    st.error(f"Prüfung fehlgeschlagen: {p}")
signature = f"{settings.kind}_{settings.n}_{settings.deg}_{settings.links}_{settings.seed}_{settings.k}"
inst = a.inst
adj = inst.adj
T = a.terminals
names = [inst.name(t) for t in T]

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
st.caption(f"{C.KIND_NAMES[kind]} mit {_i(a.n)} Standorten, {_i(a.m)} Leitungen und {_i(a.k)} Terminals ({', '.join(names)}). Standorte sind ab 1 nummeriert (das Lehrbeispiel hat Namen).")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Verfahren (isolierende Schnitte)", _i(a.cost), delta=f"Summe der k − 1 billigsten: {_i(a.approx.sum_kept)}", delta_color="off")
if a.exact:
    m2.metric("Optimum (Aufzählung)", _i(a.optimum), delta=f"{_i(a.exact.count)} von {_i(a.exact.total)} Zuordnungen", delta_color="off")
    m3.metric("Verhältnis", _r(a.ratio), delta=f"Garantie {_r(a.guarantee)}" + (" erreicht" if a.cost * a.k == (2 * a.k - 2) * a.optimum and a.cost > a.optimum else ""), delta_color="inverse" if a.cost > a.optimum else "off")
else:
    m2.metric("Optimum (Aufzählung)", "keine Aufzählung", delta=f"über {C.BRUTE_N} Standorte", delta_color="off")
    m3.metric("Höchstens das …-Fache", _r(a.lb_ratio), delta=f"Garantie {_r(a.guarantee)}", delta_color="off")
m4.metric("Untere Schranke", _i(a.approx.lower_bound), delta="Hälfte der Summe aller isolierenden Schnitte", delta_color="off")
_show(ev.verdict_multiway(a))

tab_term, tab_kcut, tab_tight = st.tabs(["🔌 Terminals trennen", "✂️ k-Schnitt", "🎯 Enge Instanz"])

# --- Tab 1: Terminals trennen --------------------------------------------------------------------------------------------------------------

with tab_term:
    which = st.selectbox("Isolierender Schnitt von Terminal", list(range(a.k)), format_func=lambda i: f"{names[i]} (Wert {_i(a.approx.cuts[i].value)})", key=f"which_{signature}",
                         help="Zeigt den kleinsten Schnitt, der dieses Terminal von allen anderen trennt (die anderen zu einer Senke zusammengezogen).")
    cut = a.approx.cuts[int(which)]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Isolierender Schnitt von {names[int(which)]}**")
        labels = tuple(int(which) if v in set(cut.side) else -1 for v in range(a.n))
        st.plotly_chart(build_map(inst, T, labels, cut.edges, height=420), width="stretch", key=f"iso_map_{signature}_{int(which)}")
        st.caption(f"Die Seite von {names[int(which)]} ({_i(len(cut.side))} Standorte) ist in der Farbe des Terminals gefärbt; rot gestrichelt die {_i(cut.value)} Leitungen des Schnitts.")
    with c2:
        st.markdown("**Alle isolierenden Schnitte**")
        rows = []
        for i, cc in enumerate(a.approx.cuts):
            rows.append({"Terminal": names[i], "Wert": _i(cc.value), "Seite (Standorte)": _i(len(cc.side)), "Rolle": "entfällt (teuerster)" if i == a.approx.dropped else "genommen"})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.caption(f"Summe aller k Werte: {_i(a.approx.total)}; Summe der k − 1 genommenen: {_i(a.approx.sum_kept)}; Vereinigung: {_i(a.cost)} Leitungen "
                   f"({'ohne Überschneidung' if a.cost == a.approx.sum_kept else f'{_i(a.approx.sum_kept - a.cost)} Leitungen liegen in zwei genommenen Schnitten'}). Untere Schranke für das Optimum: ⌈{_i(a.approx.total)} / 2⌉ = {_i(a.approx.lower_bound)}.")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(f"**Verfahren: {_i(a.cost)} Leitungen**")
        st.plotly_chart(build_map(inst, T, A.terminal_labels(adj, T, a.approx.edges), a.approx.edges, height=420), width="stretch", key=f"alg_map_{signature}")
        st.caption("Die Vereinigung der k − 1 genommenen Schnitte; jeder Standort ist in der Farbe des Terminals gefärbt, mit dem er noch verbunden ist (grau: keinem).")
    with d2:
        if a.exact:
            st.markdown(f"**Optimum: {_i(a.optimum)} Leitungen**")
            st.plotly_chart(build_map(inst, T, a.exact.labels, a.exact.edges, height=420), width="stretch", key=f"opt_map_{signature}")
            st.caption(f"Ein bester Schnitt der Aufzählung (der erste von {_i(a.exact.count)}); jeder Standort in der Farbe des Terminals, dem er zugeordnet ist.")
        else:
            st.info(f"Über {C.BRUTE_N} Standorten gibt es keine Aufzählung der Zuordnungen ({_i(a.k)}^{_i(a.n - a.k)} wären zu viele). Die untere Schranke {_i(a.approx.lower_bound)} begrenzt das Verhältnis zum Optimum auf höchstens {_r(a.lb_ratio)}.")

# --- Tab 2: k-Schnitt ---------------------------------------------------------------------------------------------------------------------

with tab_kcut:
    kg = a.kgreedy
    step = st.slider("Schritt des Greedy-Zerlegens", 0, len(kg.steps), len(kg.steps), key=f"step_{signature}", help="0: das ganze Netz, dann nach und nach die Teilungen; k − 1 Teilungen ergeben k Teile.")
    parts = A.kcut_parts_after(kg, int(step))
    owner = {v: i for i, p in enumerate(parts) for v in p}
    cross = tuple((u, v) for u, v in A.edges_of(adj) if owner[u] != owner[v])
    e1, e2 = st.columns(2)
    with e1:
        st.markdown(f"**Nach {_i(int(step))} Teilungen: {_i(len(parts))} Komponenten, {_i(len(cross))} Leitungen entfernt**")
        st.plotly_chart(build_parts_map(inst, parts, cross, height=420), width="stretch", key=f"kcut_map_{signature}_{int(step)}")
        st.caption("Jede Komponente in einer Farbe; rot gestrichelt die bisher entfernten Leitungen.")
    with e2:
        if int(step) < len(kg.steps):
            s = kg.steps[int(step)]
            st.markdown(f"**Teilung {_i(int(step) + 1)}: kleinster Schnitt je Komponente**")
            cand = []
            for comp, value in s.candidates:
                cand.append({"Komponente (Standorte)": _i(len(comp)), "Kleinster Schnitt": "nur ein Standort" if value is None else _i(value), "Gewählt": "ja" if comp == s.component else ""})
            st.dataframe(pd.DataFrame(cand), hide_index=True, width="stretch")
            st.caption(f"Geteilt wird die Komponente mit dem billigsten kleinsten Schnitt ({_i(s.value)}), bei Gleichstand die erste; die Seiten haben {_i(len(s.side))} und {_i(len(s.rest))} Standorte.")
        else:
            st.markdown("**Fertig**")
            st.write(f"{_i(a.k)} Komponenten; Gesamtkosten {_i(kg.cost)} Leitungen (Summe der Werte der Teilungen: {', '.join(_i(x.value) for x in kg.steps)}).")
    if a.kexact:
        st.markdown(f"**Optimum der Aufzählung: {_i(a.kexact.value)} Leitungen** ({_i(a.kexact.count)} von {_i(a.kexact.total)} Zerlegungen)")
        st.plotly_chart(build_parts_map(inst, a.kexact.parts, a.kexact.edges, height=360), width="stretch", key=f"kopt_map_{signature}")
        st.caption("Eine beste Zerlegung in k Teile (die erste der Aufzählung).")
    else:
        st.info(f"Über {C.BRUTE_KCUT_N} Standorten gibt es keine Aufzählung aller Zerlegungen in {_i(a.k)} Teile.")
    _show(ev.verdict_kcut(a))

# --- Tab 3: Enge Instanz ----------------------------------------------------------------------------------------------------------------------

with tab_tight:
    st.markdown("**Der Zyklus mit abwechselnden Terminals**")
    st.markdown(
        """
2k Standorte liegen auf einem Kreis, jeder zweite ist ein Terminal, jede Leitung verbindet Nachbarn. Das Verfahren trennt jedes Terminal durch **seine zwei Leitungen** (Kosten 2) und nimmt k − 1 davon: **2 (k − 1)** Leitungen.
Ein Optimum durchtrennt in jeder der k **Lücken** zwischen zwei Terminals genau eine Leitung: **k** Leitungen. Das Verhältnis ist **2 (k − 1) / k = 2 − 2/k**, die Garantie. Der Zyklus ist das Preset „Lehrbeispiel“ (k = 3) und „Die Garantie ist scharf“ (k = 4).
        """
    )
    rows_t = _tight()
    st.plotly_chart(build_tight(rows_t), width="stretch", key="tight_chart")
    tt = pd.DataFrame([{"k": _i(r["k"]), "Standorte": _i(r["n"]), "Verfahren": _i(r["alg"]), "Optimum": _i(r["opt"]), "Verhältnis": _r(r["alg"] / r["opt"]), "Garantie 2 − 2/k": _r(A.guarantee(r["k"])),
                       "Optimale Zuordnungen": f"{_i(r['count'])} von {_i(r['total'])}"} for r in rows_t])
    st.dataframe(tt, hide_index=True, width="stretch")
    _show(ev.verdict_tight(rows_t))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🔬 Experimente über feste Netze")
st.caption(f"Je Netztyp {len(C.SWEEP_SEEDS)} feste Netze mit {C.EX_N} Standorten (7 Netztypen), feste Zufalls-Seeds: nie ein einzelner Zufalls-Seed als Befund.")

st.subheader("🔬 Experiment 1: Stimmen Verfahren, Schranke und Aufzählung überein?")
rows_x = _exactness()
st.caption(f"{len(rows_x)} Netztypen mit je {len(C.SWEEP_SEEDS)} festen Netzen mit {C.EX_N} Standorten und je drei und vier Terminals; geprüft werden die Zeugnisse (Terminals getrennt), die Garantie und die untere Schranke.")
st.plotly_chart(build_exact(rows_x), width="stretch", key="ex_exact")
_show(ev.verdict_exact(rows_x))

st.subheader("🔬 Experiment 2: Wie nah liegt das Verfahren am Optimum?")
rows_r = _ratio()
st.caption(f"Kosten des Verfahrens geteilt durch das Optimum ({C.EX_N} Standorte, je Netztyp und k {len(C.SWEEP_SEEDS)} Netze): Mittel (Balken) und schlechtester Fall (Raute); gestrichelt die Garantie.")
st.plotly_chart(build_ratio(rows_r), width="stretch", key="ex_ratio")
_show(ev.verdict_ratio(rows_r))

st.subheader("🔬 Experiment 3: Der Zyklus mit abwechselnden Terminals")
st.caption("Verfahren und Optimum auf dem Zyklus für k = 2 bis 6 (Tab „Enge Instanz“): genau das Verhältnis 2 − 2/k.")
st.plotly_chart(build_tight(rows_t), width="stretch", key="ex_tight")
_show(ev.verdict_tight(rows_t))

st.subheader("🔬 Experiment 4: Im großen Netz: Kosten gegen die untere Schranke")
rows_b = _big()
st.caption(f"Bei {C.EX_BIG_N} Standorten (keine Aufzählung), {C.EX_BIG_SEEDS} Netze je Typ und k: Kosten des Verfahrens geteilt durch die untere Schranke (Mittel über die Netze); gestrichelt die Garantie.")
st.plotly_chart(build_big(rows_b), width="stretch", key="ex_big")
_show(ev.verdict_big(rows_b))

st.subheader("🔬 Experiment 5: k-Schnitt: Greedy-Zerlegen gegen die Aufzählung")
rows_k = _kcut()
st.caption(f"Anteil der Instanzen ({C.EX_KCUT_N} Standorte, je Netztyp und k {len(C.SWEEP_SEEDS)} Netze), in denen das Greedy-Zerlegen das Optimum aller Zerlegungen trifft.")
st.plotly_chart(build_kcut_rows(rows_k), width="stretch", key="ex_kcut")
_show(ev.verdict_kcut_rows(rows_k))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Alle Leitungen gleich** | Die Demo zählt Leitungen; mit Kosten je Leitung wären Schnitte gewichtete Summen (der Fluss rechnet das, die Aufzählung auch). | globaler-schnitt-demo |
| **Isolierende Schnitte statt LP-Rundung** | Das einfachste Verfahren hat die Garantie 2 − 2/k; bessere Verfahren (Rundung einer linearen Relaxation) erreichen kleinere Faktoren, sind aber nicht gebaut. | - |
| **Terminals sind gegeben** | Wer die Terminals erst wählen muss, löst eine andere Aufgabe; beim k-Schnitt gibt es keine Terminals. | - |
| **Kanten statt Knoten** | Es werden Leitungen entfernt; das Entfernen von Standorten (Knoten-Multiway-Cut) ist ein verwandtes, anderes Problem. | menger-demo |
| **Greedy-Zerlegen für den k-Schnitt** | Die Garantie 2 − 2/k gilt; für festes k gibt es exakte Verfahren in Polynomialzeit, mit hohem Exponenten (nicht gebaut). | - |
| **Synthetische Netze, bis 80 Standorte** | Reale Netze haben andere Strukturen; die Aufzählung läuft beim Multiway-Cut bis 12, beim k-Schnitt bis 10 Standorte. | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben** ein ungerichteter Graph $G = (V, E)$ mit $n$ Standorten und eine Menge von $k$ Terminals $T = \{t_1, \dots, t_k\} \subseteq V$. Ein **Multiway-Cut** ist eine Kantenmenge $F \subseteq E$, nach deren Entfernen keine zwei Terminals in derselben Komponente liegen; gesucht ist ein $F$ mit kleinstem $|F|$, das Optimum heiße $\mathrm{OPT}$.

**Aufzählung.** Jede Zuordnung $\ell : V \to T$ mit $\ell(t_i) = t_i$ liefert den Schnitt $F_\ell = \{\{u,v\} \in E : \ell(u) \ne \ell(v)\}$, und es gilt

$$\mathrm{OPT} = \min_{\ell} |F_\ell|, \qquad \text{über } k^{\,n-k} \text{ Zuordnungen.}$$

**Isolierender Schnitt.** Für $i = 1, \dots, k$ sei $F_i$ ein kleinster Schnitt zwischen $t_i$ und der Menge $T \setminus \{t_i\}$ (zu einer Senke zusammengezogen); nach dem Max-Flow-Min-Cut-Satz ist $|F_i|$ der Wert eines maximalen Flusses.

**Verfahren.** Man ordnet $|F_{(1)}| \le \dots \le |F_{(k)}|$ und nimmt $F = F_{(1)} \cup \dots \cup F_{(k-1)}$. Dann trennt $F$ alle Terminals, denn jedes Terminal außer $t_{(k)}$ ist von allen anderen getrennt.

**Untere Schranke.** Ist $F^*$ ein Optimum, so sind die Komponenten von $G - F^*$ je höchstens ein Terminal groß; sei $C_i$ die Komponente von $t_i$ und $F_i^* = \delta(C_i)$ die Menge der Randkanten. Dann ist $F_i^*$ ein Schnitt zwischen $t_i$ und den anderen Terminals, also $|F_i| \le |F_i^*|$. Jede Kante von $F^*$ liegt am Rand von höchstens zwei der Komponenten $C_i$:

$$\sum_{i=1}^{k} |F_i| \;\le\; \sum_{i=1}^{k} |F_i^*| \;\le\; 2\,\mathrm{OPT}.$$

**Garantie.** Mit $|F_{(k)}| \ge \tfrac1k \sum_i |F_i|$ folgt

$$|F| \;\le\; \sum_{i<k} |F_{(i)}| \;\le\; \Bigl(1 - \tfrac1k\Bigr) \sum_{i=1}^{k} |F_i| \;\le\; \Bigl(2 - \tfrac2k\Bigr)\,\mathrm{OPT}.$$

**Scharf.** Auf dem Zyklus mit $2k$ Standorten $t_1, v_1, \dots, t_k, v_k$ und den Terminals $t_i$ ist jedes $|F_i| = 2$ und $|F| = 2(k-1)$, während ein Schnitt mit einer Kante je Lücke $k$ Kanten hat; also $|F| / \mathrm{OPT} = 2 - 2/k$.

**k-Schnitt.** Gesucht ist ein kleinstes $F$, nach dessen Entfernen $G$ in mindestens $k$ Komponenten zerfällt. Das Greedy-Zerlegen teilt in jedem Schritt die Komponente $C$ mit dem kleinsten Wert $\lambda(G[C])$ (Stoer–Wagner) und hat Kosten höchstens $(2 - 2/k)$ mal das Optimum.

**Literatur.** E. Dahlhaus, D. S. Johnson, C. H. Papadimitriou, P. D. Seymour, M. Yannakakis: *The complexity of multiterminal cuts*, SIAM Journal on Computing 23 (4), 1994, S. 864–894. H. Saran, V. V. Vazirani: *Finding k cuts within twice the optimal*,
SIAM Journal on Computing 24 (1), 1995, S. 101–108. G. Călinescu, H. Karloff, Y. Rabani: *An improved approximation algorithm for multiway cut*, Journal of Computer and System Sciences 60 (3), 2000, S. 564–574 (Rundung einer linearen
Relaxation, Faktor 3/2 − 1/k; hier nicht gebaut). Die Demo rechnet die Flüsse mit Edmonds–Karp und die Schnitte des k-Schnitts mit Stoer–Wagner, ohne Gewichte.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
