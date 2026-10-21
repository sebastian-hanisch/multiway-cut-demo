"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import mwc_algorithm as A
import mwc_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _lines(inst, pairs):
    xs, ys = [], []
    for u, v in pairs:
        xs += [float(inst.xy[u, 0]), float(inst.xy[v, 0]), None]
        ys += [float(inst.xy[u, 1]), float(inst.xy[v, 1]), None]
    return xs, ys


def _map_layout(fig, inst, height=470):
    xs, ys = inst.xy[:, 0], inst.xy[:, 1]
    pad = 0.25 * max(float(xs.max() - xs.min()), float(ys.max() - ys.min()), 1.0)
    fig.update_xaxes(visible=False, range=[float(xs.min()) - pad, float(xs.max()) + pad])
    fig.update_yaxes(visible=False, range=[float(ys.min()) - pad, float(ys.max()) + pad])
    return _base(fig, height)


def color_of(label):
    return C.COLOR_FREE if label < 0 else C.COLOR_TERMINALS[label % len(C.COLOR_TERMINALS)]


def build_map(inst, terminals, labels=None, cut_edges=(), height=470):
    """Karte: Terminals als Rauten in je einer Farbe, die übrigen Standorte in der Farbe des Terminals, dem sie zugeordnet sind (grau: keinem), die Leitungen des Schnitts rot gestrichelt."""
    n = inst.n
    labels = tuple(labels) if labels is not None else (-1,) * n
    cut = {(min(u, v), max(u, v)) for u, v in cut_edges}
    rest = [(u, v) for u, v in inst.pairs if (u, v) not in cut]
    fig = go.Figure()
    xs, ys = _lines(inst, rest)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_EDGE, width=1.2), hoverinfo="skip", showlegend=False))
    xs, ys = _lines(inst, sorted(cut))
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_CUT, width=2.8, dash="dot"), hoverinfo="skip", name=f"Schnitt ({len(cut)})"))
    show_text = n <= 60
    size = 22 if show_text else 11
    tset = set(terminals)
    free = [v for v in range(n) if v not in tset]
    fig.add_trace(go.Scatter(
        x=[float(inst.xy[v, 0]) for v in free], y=[float(inst.xy[v, 1]) for v in free], mode="markers+text" if show_text else "markers",
        marker=dict(size=size, color=[color_of(labels[v]) for v in free], line=dict(color="white", width=1)), text=[inst.name(v) for v in free] if show_text else None, textfont=dict(size=10, color="#222222"),
        textposition="middle center", hovertext=[f"Standort {inst.name(v)}" for v in free], hoverinfo="text", name="Standort"))
    fig.add_trace(go.Scatter(
        x=[float(inst.xy[t, 0]) for t in terminals], y=[float(inst.xy[t, 1]) for t in terminals], mode="markers+text" if show_text else "markers",
        marker=dict(size=size + 8, symbol="diamond", color=[color_of(i) for i in range(len(terminals))], line=dict(color="white", width=2)), text=[inst.name(t) for t in terminals] if show_text else None,
        textfont=dict(size=10, color="#ffffff"), textposition="middle center", hovertext=[f"Terminal {inst.name(t)}" for t in terminals], hoverinfo="text", name="Terminal"))
    return _map_layout(fig, inst, height)


def build_parts_map(inst, parts, cut_edges=(), height=470):
    """Karte für den k-Schnitt: jeder Teil in einer Farbe."""
    labels = [-1] * inst.n
    for i, part in enumerate(parts):
        for v in part:
            labels[v] = i
    return build_map(inst, (), labels, cut_edges, height)


# --- Experimente ---------------------------------------------------------------------------------------------------------------------------------


def build_tight(rows):
    ks = [r["k"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ks, y=[r["alg"] for r in rows], name="Verfahren (isolierende Schnitte)", marker_color=C.COLOR_BAR2, hovertemplate="k = %{x}: %{y} Leitungen<extra></extra>"))
    fig.add_trace(go.Bar(x=ks, y=[r["opt"] for r in rows], name="Optimum (Aufzählung)", marker_color=C.COLOR_BAR3, hovertemplate="k = %{x}: %{y} Leitungen<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(title_text="Zahl der Terminals k", dtick=1)
    fig.update_yaxes(title_text="Leitungen im Schnitt", rangemode="tozero")
    return _base(fig)


def build_exact(rows):
    ys = [round(100 * (r["checks"] - r["wrong"]) / r["checks"]) if r["checks"] else 0 for r in rows]
    fig = go.Figure(go.Bar(x=[r["label"] for r in rows], y=ys, marker_color=C.COLOR_BAR, showlegend=False, hovertemplate="%{x}: %{y} %<extra></extra>"))
    fig.update_yaxes(title_text="Prüfungen ohne Abweichung (%)", range=[0, 105])
    return _base(fig)


def _by_k(rows, ks):
    labels = []
    for r in rows:
        if r["label"] not in labels:
            labels.append(r["label"])
    return labels, {k: {r["label"]: r for r in rows if r["k"] == k} for k in ks}


def build_ratio(rows):
    ks = sorted({r["k"] for r in rows})
    labels, by = _by_k(rows, ks)
    fig = go.Figure()
    for k, color in zip(ks, (C.COLOR_BAR, C.COLOR_BAR2)):
        fig.add_trace(go.Bar(x=labels, y=[round(by[k][lb]["sum_ratio"] / by[k][lb]["nets"], 3) for lb in labels], name=f"Mittel, k = {k}", marker_color=color, hovertemplate="%{x}: %{y}<extra></extra>"))
    for k, color in zip(ks, (C.COLOR_BAR, C.COLOR_BAR2)):
        fig.add_trace(go.Scatter(x=labels, y=[by[k][lb]["max_ratio"] for lb in labels], mode="markers", marker=dict(size=10, symbol="diamond", color=color, line=dict(color="white", width=1)), name=f"schlechtestes, k = {k}",
                                 hovertemplate="%{x}: %{y:.2f}<extra></extra>"))
    for k in ks:
        fig.add_hline(y=A.guarantee(k), line=dict(color=C.COLOR_CUT, dash="dash", width=1.5), annotation_text=f"Garantie k = {k}", annotation_position="top left")
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Kosten des Verfahrens / Optimum", range=[0.95, 1.6])
    return _base(fig, 400)


def build_big(rows):
    ks = sorted({r["k"] for r in rows})
    labels, by = _by_k(rows, ks)
    fig = go.Figure()
    for k, color in zip(ks, (C.COLOR_BAR, C.COLOR_BAR2)):
        fig.add_trace(go.Bar(x=labels, y=[round(by[k][lb]["sum_alg"] / by[k][lb]["sum_lb"], 3) for lb in labels], name=f"Mittel, k = {k}", marker_color=color, hovertemplate="%{x}: %{y}<extra></extra>"))
    for k in ks:
        fig.add_hline(y=A.guarantee(k), line=dict(color=C.COLOR_CUT, dash="dash", width=1.5), annotation_text=f"Garantie k = {k}", annotation_position="top left")
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Kosten / untere Schranke", range=[0.95, 1.6])
    return _base(fig, 380)


def build_kcut_rows(rows):
    ks = sorted({r["k"] for r in rows})
    labels, by = _by_k(rows, ks)
    fig = go.Figure()
    for k, color in zip(ks, (C.COLOR_BAR, C.COLOR_BAR2)):
        fig.add_trace(go.Bar(x=labels, y=[round(100 * by[k][lb]["exact"] / by[k][lb]["nets"]) for lb in labels], name=f"k = {k}", marker_color=color, hovertemplate="%{x}: %{y} %<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Instanzen, in denen Greedy-Zerlegen optimal ist (%)", range=[0, 105])
    return _base(fig, 380)
