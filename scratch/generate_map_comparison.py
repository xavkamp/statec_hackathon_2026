import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.dashboard.data_loader import load_partner_rankings, load_product_partners
from src.dashboard.design_system import apply_map_theme, add_iso3_column
from src.dashboard.app import get_country_name
import numpy as np

# Load real data
df = load_partner_rankings()
sub = df[(df["year"] == 2025) & (df["flow"] == "IMPORT")].copy()
sub_map = add_iso3_column(sub).dropna(subset=["iso3"]).copy()
sub_map["color_val"] = np.log10(np.maximum(10000.0, sub_map["value_eur"]))

def make_map(scope, center_lux=False):
    fig = go.Figure(go.Choropleth(
        locations=sub_map["iso3"],
        z=sub_map["color_val"],
        text=sub_map["partner_code"].apply(get_country_name),
        colorscale=[[0.0, "#EDE9FE"], [0.2, "#DDD6FE"], [0.4, "#A78BFA"], [0.65, "#6366F1"], [0.85, "#4338CA"], [1.0, "#1E1B4B"]],
        showscale=False
    ))
    apply_map_theme(fig, scope=scope)
    if center_lux:
        fig.update_geos(center=dict(lat=49.8153, lon=6.1296))
    fig.update_layout(title=f"Scope: {scope} | Centered on Lux: {center_lux}", height=380, margin=dict(l=0, r=0, t=40, b=0))
    return fig

f_eu_def = make_map("europe", center_lux=False)
f_eu_lux = make_map("europe", center_lux=True)
f_wo_def = make_map("world", center_lux=False)
f_wo_lux = make_map("world", center_lux=True)

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Map Centering Comparison</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        body {{ font-family: Inter, sans-serif; background: #F8FAFC; margin: 20px; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <h2>Map Centering Comparison: Default vs Centered on Luxembourg (49.8153° N, 6.1296° E)</h2>
    <div class="grid">
        <div class="card">{f_eu_def.to_html(full_html=False, include_plotlyjs=False)}</div>
        <div class="card">{f_eu_lux.to_html(full_html=False, include_plotlyjs=False)}</div>
        <div class="card">{f_wo_def.to_html(full_html=False, include_plotlyjs=False)}</div>
        <div class="card">{f_wo_lux.to_html(full_html=False, include_plotlyjs=False)}</div>
    </div>
</body>
</html>
"""

output_path = BASE_DIR / "scratch" / "test_map_visual.html"
output_path.write_text(html_content, encoding="utf-8")
print(f"Generated {output_path}")
