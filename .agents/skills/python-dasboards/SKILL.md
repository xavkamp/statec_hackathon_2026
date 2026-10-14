---
name: python-dashboards
description: >
  Build beautiful, production-quality interactive dashboards in Python using Plotly and Dash.
  Covers design systems, color palettes, typography, layout, chart polish, KPI cards, filters,
  and export. Use this skill whenever the user wants to create a dashboard, data app, interactive
  visualization, or reporting UI in Python — even if they just say "make this look good" or "build
  a viz". Always trigger for requests involving Plotly, Dash, panel, streamlit charts, or any
  Python-based interactive data display. Trigger even for single-chart polish requests: if the
  user wants a chart that looks professional, not default-matplotlib-ugly, use this skill.
  Prefer this skill over generic pandas/matplotlib advice whenever aesthetics or interactivity matter.
---

# Python Dashboards Skill

A skill for building dashboards that look designed, not generated — using Plotly for charts and
Dash for interactive apps, with an opinionated design system that produces consistently beautiful results.

---

## Framework Selection

| Need | Use |
|------|-----|
| Interactive standalone app (filters, callbacks, multi-page) | **Dash** |
| Single-page exploratory notebook / quick share | **Plotly + Jupyter** or **Streamlit** |
| Static report charts (PDF/PNG export) | **Plotly static export** via kaleido |
| Embedded in existing web app | **Plotly.js** via `plotly.offline` |

This skill focuses on **Plotly + Dash**. For Streamlit, the chart patterns in Stage 3 apply identically — just swap the layout wiring.

---

## Stage 1 — Design System

Establish these constants at the top of every project. Never hardcode colors or fonts inline.

```python
# design_system.py  (import this everywhere)

# ── Palette ────────────────────────────────────────────────────────────────
PRIMARY       = "#2563EB"   # blue-600   — primary action / highlight
SUCCESS       = "#16A34A"   # green-600  — positive delta, up trend
DANGER        = "#DC2626"   # red-600    — negative delta, alert
WARNING       = "#D97706"   # amber-600  — caution
NEUTRAL       = "#6B7280"   # gray-500   — secondary text, gridlines
SURFACE       = "#F9FAFB"   # gray-50    — card / panel background
BACKGROUND    = "#FFFFFF"   # page background
BORDER        = "#E5E7EB"   # gray-200   — card borders, dividers
TEXT_PRIMARY  = "#111827"   # gray-900
TEXT_SECONDARY= "#6B7280"   # gray-500

# Categorical sequence (colorblind-safe, 8 colors)
CATEGORICAL = [
    "#2563EB", "#16A34A", "#D97706", "#DC2626",
    "#7C3AED", "#0891B2", "#DB2777", "#65A30D",
]

# Sequential (light → dark, for heatmaps / choropleth)
SEQUENTIAL = ["#DBEAFE", "#93C5FD", "#3B82F6", "#1D4ED8", "#1E3A8A"]

# Diverging (red → white → blue, for deltas)
DIVERGING = ["#DC2626", "#FCA5A5", "#F9FAFB", "#93C5FD", "#2563EB"]

# ── Typography ──────────────────────────────────────────────────────────────
FONT_FAMILY   = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
FONT_SIZE_XS  = 10
FONT_SIZE_SM  = 12
FONT_SIZE_MD  = 14
FONT_SIZE_LG  = 16
FONT_SIZE_XL  = 20
FONT_SIZE_2XL = 24

# ── Spacing ─────────────────────────────────────────────────────────────────
PADDING_SM    = "12px"
PADDING_MD    = "20px"
PADDING_LG    = "32px"
RADIUS_SM     = "6px"
RADIUS_MD     = "10px"
RADIUS_LG     = "16px"

# ── Shadows ─────────────────────────────────────────────────────────────────
SHADOW_SM = "0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04)"
SHADOW_MD = "0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.05)"
SHADOW_LG = "0 10px 15px rgba(0,0,0,0.08), 0 4px 6px rgba(0,0,0,0.04)"
```

### Base Plotly layout template

Apply this to every figure — it replaces Plotly's default grey look.

```python
import plotly.graph_objects as go
import plotly.io as pio
from design_system import *

BASE_LAYOUT = dict(
    font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY, size=FONT_SIZE_MD),
    paper_bgcolor=BACKGROUND,
    plot_bgcolor=BACKGROUND,
    colorway=CATEGORICAL,
    margin=dict(l=48, r=24, t=48, b=40),
    title=dict(
        font=dict(size=FONT_SIZE_LG, color=TEXT_PRIMARY, family=FONT_FAMILY),
        x=0.0, xanchor="left", pad=dict(l=0, b=8),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
        font=dict(size=FONT_SIZE_SM, color=TEXT_SECONDARY),
        orientation="h",
        yanchor="bottom", y=1.02, xanchor="left", x=0,
    ),
    xaxis=dict(
        showgrid=False,
        linecolor=BORDER,
        tickfont=dict(size=FONT_SIZE_SM, color=TEXT_SECONDARY),
        title_font=dict(size=FONT_SIZE_SM, color=TEXT_SECONDARY),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor=BORDER,
        gridwidth=1,
        zeroline=False,
        linecolor="rgba(0,0,0,0)",
        tickfont=dict(size=FONT_SIZE_SM, color=TEXT_SECONDARY),
        title_font=dict(size=FONT_SIZE_SM, color=TEXT_SECONDARY),
    ),
    hoverlabel=dict(
        bgcolor=TEXT_PRIMARY,
        font_color=BACKGROUND,
        font_size=FONT_SIZE_SM,
        bordercolor=TEXT_PRIMARY,
    ),
)

# Register as a named template
pio.templates["clean"] = go.layout.Template(layout=BASE_LAYOUT)
pio.templates.default = "clean"
```

---

## Stage 2 — Layout & Structure (Dash)

### App scaffold

```python
# app.py
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from design_system import *

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
    suppress_callback_exceptions=True,
)

app.layout = html.Div(
    style={"backgroundColor": BACKGROUND, "minHeight": "100vh", "fontFamily": FONT_FAMILY},
    children=[
        _header(),
        html.Div(
            style={"maxWidth": "1280px", "margin": "0 auto", "padding": f"24px {PADDING_LG}"},
            children=[
                _kpi_row(),
                html.Div(style={"height": "24px"}),
                _chart_grid(),
            ],
        ),
    ],
)
```

### KPI card component

```python
def kpi_card(title: str, value: str, delta: str = None, delta_positive: bool = True) -> html.Div:
    delta_color = SUCCESS if delta_positive else DANGER
    delta_icon  = "▲" if delta_positive else "▼"
    return html.Div(
        style={
            "backgroundColor": SURFACE,
            "borderRadius": RADIUS_MD,
            "padding": PADDING_MD,
            "boxShadow": SHADOW_SM,
            "border": f"1px solid {BORDER}",
            "minWidth": "180px",
            "flex": "1",
        },
        children=[
            html.P(title, style={
                "margin": "0 0 4px 0", "fontSize": f"{FONT_SIZE_SM}px",
                "color": TEXT_SECONDARY, "fontWeight": "500", "textTransform": "uppercase",
                "letterSpacing": "0.05em",
            }),
            html.P(value, style={
                "margin": "0", "fontSize": f"{FONT_SIZE_2XL}px",
                "color": TEXT_PRIMARY, "fontWeight": "700", "lineHeight": "1.2",
            }),
            html.P(f"{delta_icon} {delta}", style={
                "margin": "6px 0 0 0", "fontSize": f"{FONT_SIZE_SM}px",
                "color": delta_color, "fontWeight": "500",
            }) if delta else None,
        ],
    )

def _kpi_row() -> html.Div:
    return html.Div(
        style={"display": "flex", "gap": "16px", "flexWrap": "wrap"},
        children=[
            kpi_card("Total Revenue",   "$2.4M",  "+12% vs last month",  True),
            kpi_card("Active Users",    "18,420", "+5.3% vs last month",  True),
            kpi_card("Churn Rate",      "3.1%",   "+0.4pp vs last month", False),
            kpi_card("Avg Order Value", "$130",   "-2.1% vs last month",  False),
        ],
    )
```

### Two-column chart grid

```python
def chart_card(figure, title: str = None) -> html.Div:
    return html.Div(
        style={
            "backgroundColor": SURFACE,
            "borderRadius": RADIUS_MD,
            "padding": PADDING_MD,
            "boxShadow": SHADOW_SM,
            "border": f"1px solid {BORDER}",
        },
        children=[
            html.P(title, style={
                "margin": "0 0 12px 0", "fontSize": f"{FONT_SIZE_MD}px",
                "color": TEXT_PRIMARY, "fontWeight": "600",
            }) if title else None,
            dcc.Graph(figure=figure, config={"displayModeBar": False}),
        ],
    )

def _chart_grid() -> html.Div:
    return html.Div(
        style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"},
        children=[
            chart_card(make_revenue_chart(), "Revenue Over Time"),
            chart_card(make_breakdown_chart(), "Revenue by Channel"),
            chart_card(make_funnel_chart(), "Conversion Funnel"),
            chart_card(make_heatmap(), "Activity Heatmap"),
        ],
    )
```

---

## Stage 3 — Chart Recipes

### Line chart (trend)

```python
import plotly.graph_objects as go
import pandas as pd
from design_system import *

def make_line_chart(df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y],
        mode="lines",
        line=dict(color=PRIMARY, width=2.5),
        fill="tozeroy",
        fillcolor=f"rgba(37, 99, 235, 0.08)",    # PRIMARY at 8% opacity
        hovertemplate=f"<b>%{{x}}</b><br>{y}: %{{y:,.0f}}<extra></extra>",
    ))
    # Add a subtle dot on the last data point
    fig.add_trace(go.Scatter(
        x=[df[x].iloc[-1]], y=[df[y].iloc[-1]],
        mode="markers",
        marker=dict(color=PRIMARY, size=8, line=dict(color=BACKGROUND, width=2)),
        showlegend=False, hoverinfo="skip",
    ))
    fig.update_layout(title=title, showlegend=False)
    return fig
```

### Bar chart (comparison)

```python
def make_bar_chart(df: pd.DataFrame, x: str, y: str, title: str,
                   horizontal: bool = False) -> go.Figure:
    # Sort descending for ranked comparison
    df = df.sort_values(y, ascending=horizontal)
    fig = go.Figure(go.Bar(
        x=df[y] if horizontal else df[x],
        y=df[x] if horizontal else df[y],
        orientation="h" if horizontal else "v",
        marker=dict(
            color=df[y],
            colorscale=[[0, f"rgba(37,99,235,0.3)"], [1, PRIMARY]],
            showscale=False,
        ),
        text=df[y].apply(lambda v: f"${v/1e6:.1f}M" if v >= 1e6 else f"{v:,.0f}"),
        textposition="outside" if horizontal else "outside",
        textfont=dict(size=FONT_SIZE_SM, color=TEXT_SECONDARY),
        hovertemplate=f"<b>%{{{'y' if horizontal else 'x'}}}</b><br>{y}: %{{{'x' if horizontal else 'y'}:,.0f}}<extra></extra>",
    ))
    axis_update = dict(showgrid=False, tickfont=dict(size=FONT_SIZE_SM))
    if horizontal:
        fig.update_xaxes(showticklabels=False, **axis_update)
        fig.update_yaxes(**axis_update)
    else:
        fig.update_xaxes(**axis_update)
    fig.update_layout(title=title, bargap=0.35)
    return fig
```

### Donut chart (composition)

```python
def make_donut(labels: list, values: list, title: str, center_text: str = None) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.65,
        marker=dict(colors=CATEGORICAL, line=dict(color=BACKGROUND, width=3)),
        textinfo="label+percent",
        textfont=dict(size=FONT_SIZE_SM),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>",
    ))
    if center_text:
        fig.add_annotation(
            text=center_text, x=0.5, y=0.5, showarrow=False,
            font=dict(size=FONT_SIZE_XL, color=TEXT_PRIMARY, family=FONT_FAMILY),
        )
    fig.update_layout(title=title, showlegend=True)
    return fig
```

### Funnel chart

```python
def make_funnel(stages: list[str], values: list[int], title: str) -> go.Figure:
    fig = go.Figure(go.Funnel(
        y=stages, x=values,
        textinfo="value+percent initial",
        textfont=dict(size=FONT_SIZE_SM, color=BACKGROUND),
        marker=dict(color=CATEGORICAL[:len(stages)]),
        connector=dict(line=dict(color=BORDER, width=2)),
    ))
    fig.update_layout(title=title)
    return fig
```

### Heatmap (calendar / matrix)

```python
def make_heatmap(z: list, x: list, y: list, title: str) -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=z, x=x, y=y,
        colorscale=[[0, SURFACE], [0.5, "#93C5FD"], [1, PRIMARY]],
        showscale=True,
        hovertemplate="<b>%{x} / %{y}</b><br>Value: %{z:,.0f}<extra></extra>",
        xgap=2, ygap=2,           # gap between cells = grid effect
    ))
    fig.update_layout(title=title)
    fig.update_xaxes(side="bottom", tickfont=dict(size=FONT_SIZE_XS))
    fig.update_yaxes(tickfont=dict(size=FONT_SIZE_XS))
    return fig
```

---

## Stage 4 — Filters & Interactivity (Dash Callbacks)

### Filter bar component

```python
def filter_bar(date_options: list, segment_options: list) -> html.Div:
    dropdown_style = {
        "fontSize": f"{FONT_SIZE_SM}px", "borderRadius": RADIUS_SM,
        "border": f"1px solid {BORDER}", "minWidth": "160px",
    }
    return html.Div(
        style={
            "display": "flex", "gap": "12px", "alignItems": "center",
            "padding": f"12px {PADDING_MD}",
            "backgroundColor": SURFACE, "borderBottom": f"1px solid {BORDER}",
            "flexWrap": "wrap",
        },
        children=[
            html.Span("Filter by:", style={"color": TEXT_SECONDARY, "fontSize": f"{FONT_SIZE_SM}px", "fontWeight": "500"}),
            dcc.Dropdown(id="date-filter",    options=date_options,    value=date_options[0]["value"],    clearable=False, style=dropdown_style),
            dcc.Dropdown(id="segment-filter", options=segment_options, value=None, placeholder="All segments", style=dropdown_style),
        ],
    )
```

### Callback pattern

```python
from dash import callback, Input, Output

@callback(
    Output("revenue-chart", "figure"),
    Output("breakdown-chart", "figure"),
    Input("date-filter",    "value"),
    Input("segment-filter", "value"),
)
def update_charts(date_range: str, segment: str):
    df = load_data()                              # load or query fresh
    if date_range == "30d":
        df = df[df.date >= pd.Timestamp.now() - pd.Timedelta(days=30)]
    if segment:
        df = df[df.segment == segment]
    return make_line_chart(df, "date", "revenue", "Revenue"), \
           make_bar_chart(df.groupby("channel", as_index=False)["revenue"].sum(),
                          "channel", "revenue", "By Channel", horizontal=True)
```

---

## Stage 5 — Polish & Export

### Annotation & reference lines

```python
# Add a target / benchmark line
fig.add_hline(
    y=target_value,
    line=dict(color=WARNING, width=1.5, dash="dot"),
    annotation_text="Target",
    annotation_font=dict(color=WARNING, size=FONT_SIZE_XS),
    annotation_position="right",
)

# Highlight a date range (e.g., promo period)
fig.add_vrect(
    x0="2024-03-01", x1="2024-03-14",
    fillcolor=f"rgba(37,99,235,0.06)",
    line_width=0,
    annotation_text="Promo", annotation_position="top left",
    annotation_font=dict(size=FONT_SIZE_XS, color=PRIMARY),
)
```

### Axis formatting

```python
# Currency
fig.update_yaxes(tickprefix="$", tickformat=",.0f")

# Percentage
fig.update_yaxes(ticksuffix="%", tickformat=".1f")

# Large numbers (K / M)
fig.update_yaxes(tickformat=".2s")   # 1.2M, 430K

# Date axis — show month abbrev
fig.update_xaxes(dtick="M1", tickformat="%b '%y")
```

### Responsive sizing

```python
# Always set responsive=True in Graph component
dcc.Graph(
    figure=fig,
    responsive=True,
    style={"height": "320px"},
    config={"displayModeBar": False, "responsive": True},
)

# In figure layout — use relative sizing
fig.update_layout(
    autosize=True,
    height=320,
    margin=dict(l=40, r=16, t=40, b=32),
)
```

### Static export (PNG / PDF)

```python
# Requires: pip install kaleido
fig.write_image("chart.png", width=1200, height=600, scale=2)   # retina
fig.write_image("chart.pdf", width=1200, height=600)
fig.write_html("chart.html", include_plotlyjs="cdn")             # self-contained HTML
```

### Dark mode variant

```python
DARK = dict(
    paper_bgcolor="#0F172A",
    plot_bgcolor="#0F172A",
    font=dict(color="#F1F5F9"),
    xaxis=dict(linecolor="#334155", tickfont=dict(color="#94A3B8")),
    yaxis=dict(gridcolor="#1E293B", tickfont=dict(color="#94A3B8")),
)
fig.update_layout(**DARK)
```

---

## Design Principles

**1. One insight per chart** — if a chart needs a legend with 8 items, split it into two charts.

**2. Remove to improve** — eliminate every element that isn't carrying information: tick marks, borders, backgrounds, unnecessary gridlines.

**3. Lead with the insight in the title** — "Revenue up 12% MoM" beats "Revenue Over Time".

**4. Consistent color semantics** — use `SUCCESS` for positive always, `DANGER` for negative always. Never reuse a semantic color for a non-semantic purpose.

**5. Align numbers right, labels left** — in tables and KPI cards; it makes scanning fast.

**6. Use white space** — add `gap`, `padding`, and `margin` generously; crowded dashboards feel untrustworthy.

**7. Mobile-first sizing** — test at 375px width; if it breaks, use `flexWrap: "wrap"` and `minWidth` on cards.

---

## Quick-Reference: Package Install

```bash
pip install dash dash-bootstrap-components plotly pandas kaleido
```

| Package | Purpose |
|---------|---------|
| `plotly` | All chart types |
| `dash` | Web app framework |
| `dash-bootstrap-components` | Bootstrap grid + components for layout |
| `kaleido` | Static PNG/PDF export from Plotly |
| `pandas` | Data manipulation |
