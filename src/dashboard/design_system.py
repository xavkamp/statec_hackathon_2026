"""Design System tokens and Plotly figure templates for STATEC Hackathon 2026.
Follows clean modern typography and accessible color palettes.
"""

# Palette
PRIMARY = "#0284C7"       # Sky-600 — Primary brand / Exports
SECONDARY = "#4F46E5"     # Indigo-600 — Imports
SUCCESS = "#10B981"       # Emerald-500 — Surplus / Growth
DANGER = "#EF4444"        # Red-500 — Deficit / Decline
WARNING = "#F59E0B"       # Amber-500 — Caution / Secondary
NEUTRAL = "#64748B"       # Slate-500 — Axis labels, captions
SURFACE = "#FFFFFF"       # White card background
BACKGROUND = "#F8FAFC"    # Slate-50 app background
BORDER = "#E2E8F0"        # Slate-200 card borders
TEXT_PRIMARY = "#0F172A"  # Slate-900
TEXT_MUTED = "#64748B"    # Slate-500

# Categorical sequence (Colorblind-safe)
CATEGORICAL = [
    "#0284C7", "#4F46E5", "#10B981", "#F59E0B", "#EC4899",
    "#8B5CF6", "#14B8A6", "#F97316", "#6366F1", "#84CC16"
]

# Plotly Template Default Layout
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color=TEXT_PRIMARY, size=12),
    margin=dict(l=40, r=30, t=50, b=40),
    hoverlabel=dict(
        bgcolor="#1E293B",
        font_size=12,
        font_color="#F8FAFC",
        font_family="Inter, sans-serif"
    ),
    xaxis=dict(
        gridcolor="#F1F5F9",
        zerolinecolor="#E2E8F0",
        tickfont=dict(color=NEUTRAL, size=11),
        title_font=dict(color=TEXT_PRIMARY, size=12, weight="bold")
    ),
    yaxis=dict(
        gridcolor="#F1F5F9",
        zerolinecolor="#E2E8F0",
        tickfont=dict(color=NEUTRAL, size=11),
        title_font=dict(color=TEXT_PRIMARY, size=12, weight="bold")
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(color=NEUTRAL, size=11)
    )
)

# Custom CSS styling dictionary
CARD_STYLE = {
    "backgroundColor": SURFACE,
    "borderRadius": "12px",
    "border": f"1px solid {BORDER}",
    "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)",
    "padding": "20px",
    "marginBottom": "20px"
}

KPI_CARD_STYLE = {
    "backgroundColor": SURFACE,
    "borderRadius": "12px",
    "border": f"1px solid {BORDER}",
    "boxShadow": "0 2px 4px 0 rgba(0, 0, 0, 0.04)",
    "padding": "18px 22px",
    "height": "100%"
}
