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
    apply_map_theme(fig, scope=update_geo_kwargs.get("scope", "europe"))
    fig.update_geos(**update_geo_kwargs)
    fig.update_layout(title=title, height=360, margin=dict(l=0, r=0, t=35, b=0))
    return fig

# Variations to test:
# 1. Europe default
m1 = make_test_map("Europe Default", {"scope": "europe"})
# 2. Europe center lat 49.8, lon 6.13
m2 = make_test_map("Europe Center (lat=49.8, lon=6.13)", {"scope": "europe", "center": dict(lat=49.8153, lon=6.1296)})
# 3. Europe center lat 51.5, lon 6.13 (slightly adjusted so Scandinavia & Iberia are both balanced)
m3 = make_test_map("Europe Balanced (lat=51.5, lon=6.13, scale=1.1)", {"scope": "europe", "center": dict(lat=51.5, lon=6.1296), "projection_scale": 1.1})

# 4. World Default
m4 = make_test_map("World Default", {"scope": "world"})
# 5. World rotated to Lux meridian (lon=6.13)
m5 = make_test_map("World Rotated (lon=6.13)", {"scope": "world", "projection_rotation": dict(lon=6.1296)})
# 6. World Center (lat=20, lon=6.13)
m6 = make_test_map("World Center (lat=20, lon=6.13)", {"scope": "world", "center": dict(lat=20, lon=6.1296)})

html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Map Centering Detailed Comparison</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        body {{ font-family: Inter, sans-serif; background: #F1F5F9; margin: 15px; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }}
        .card {{ background: white; border-radius: 8px; padding: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <h3>Europe Map Variations</h3>
    <div class="grid">
        <div class="card">{m1.to_html(full_html=False, include_plotlyjs=False)}</div>
        <div class="card">{m2.to_html(full_html=False, include_plotlyjs=False)}</div>
        <div class="card">{m3.to_html(full_html=False, include_plotlyjs=False)}</div>
    </div>
    <h3 style="margin-top:20px;">World Map Variations</h3>
    <div class="grid">
        <div class="card">{m4.to_html(full_html=False, include_plotlyjs=False)}</div>
        <div class="card">{m5.to_html(full_html=False, include_plotlyjs=False)}</div>
        <div class="card">{m6.to_html(full_html=False, include_plotlyjs=False)}</div>
    </div>
</body>
</html>
"""

output_path = BASE_DIR / "scratch" / "test_map_variations.html"
output_path.write_text(html, encoding="utf-8")
print(f"Generated {output_path}")
