import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.dashboard.data_loader import load_partner_rankings
from src.dashboard.design_system import apply_map_theme, add_iso3_column
from src.dashboard.app import get_country_name
import numpy as np

df = load_partner_rankings()
sub = df[(df["year"] == 2025) & (df["flow"] == "IMPORT")].copy()
sub_map = add_iso3_column(sub).dropna(subset=["iso3"]).copy()
sub_map["color_val"] = np.log10(np.maximum(10000.0, sub_map["value_eur"]))

def make_test_map(title, update_geo_kwargs):
    fig = go.Figure(go.Choropleth(
        locations=sub_map["iso3"],
        z=sub_map["color_val"],
        text=sub_map["partner_code"].apply(get_country_name),
        colorscale=[[0.0, "#EDE9FE"], [0.2, "#DDD6FE"], [0.4, "#A78BFA"], [0.65, "#6366F1"], [0.85, "#4338CA"], [1.0, "#1E1B4B"]],
        showscale=False
    ))
    apply_map_theme(fig, scope="europe")
    fig.update_geos(**update_geo_kwargs)
    fig.update_layout(title=title, height=400, margin=dict(l=0, r=0, t=35, b=0))
    return fig

# Option A: Scope europe with direct center (lat=49.8153, lon=6.1296)
mA = make_test_map("Option A: scope='europe', center=(49.8153, 6.1296)", {
    "scope": "europe",
    "center": dict(lat=49.8153, lon=6.1296)
})

# Option B: Scope europe with projection_scale=1.15 and center=(49.8153, 6.1296)
mB = make_test_map("Option B: scope='europe', scale=1.15, center=(49.8153, 6.1296)", {
    "scope": "europe",
    "projection_scale": 1.15,
    "center": dict(lat=49.8153, lon=6.1296)
})

# Option C: Scope world with center and range focused on Europe around Lux
mC = make_test_map("Option C: scope='world', lat=[34, 71], lon=[-22, 34]", {
    "scope": "world",
    "projection_type": "mercator",
    "center": dict(lat=49.8153, lon=6.1296),
    "lataxis_range": [34, 71],
    "lonaxis_range": [-22, 34]
})

html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Europe Centering Options</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        body {{ font-family: Inter, sans-serif; background: #F1F5F9; margin: 15px; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }}
        .card {{ background: white; border-radius: 8px; padding: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <h3>Europe Map Fine-Tuning</h3>
    <div class="grid">
        <div class="card">{mA.to_html(full_html=False, include_plotlyjs=False)}</div>
        <div class="card">{mB.to_html(full_html=False, include_plotlyjs=False)}</div>
        <div class="card">{mC.to_html(full_html=False, include_plotlyjs=False)}</div>
    </div>
</body>
</html>
"""

output_path = BASE_DIR / "scratch" / "test_europe_options.html"
output_path.write_text(html, encoding="utf-8")
print(f"Generated {output_path}")
