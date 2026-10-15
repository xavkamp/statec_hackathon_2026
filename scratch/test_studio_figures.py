import sys
sys.path.insert(0, '.')
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from src.dashboard.data_loader import (
    load_partner_rankings,
    load_product_rankings,
    load_product_partners,
    load_hs4_product_rankings,
    load_drilldown_lvl2,
    load_drilldown_lvl4,
    load_drilldown_lvl8,
)
from src.dashboard.design_system import (
    PRIMARY, SECONDARY, STATEC_BLUE, STATEC_NAVY, STATEC_RED,
    STATEC_YELLOW, STATEC_GRAY, BORDER, SUCCESS, WARNING, DANGER,
    apply_plot_theme, apply_map_theme, add_iso3_column, ISO2_TO_ISO3, fmt_eur, fmt_pct
)

# Test building map figure
def test_map():
    partners_df = load_partner_rankings()
    year = 2024
    flow = "IMPORT"
    selected_partner = "DE"
    
    sub = partners_df[(partners_df["year"] == year) & (partners_df["flow"] == flow)].copy()
    sub = add_iso3_column(sub)
    sub_valid = sub.dropna(subset=["iso3"]).copy()
    
    sub_valid["color_val"] = np.log10(np.maximum(10000.0, sub_valid["value_eur"]))
    cmin = 6.0
    cmax = max(7.0, sub_valid["color_val"].max())
    
    fig = go.Figure(go.Choropleth(
        locations=sub_valid["iso3"],
        z=sub_valid["color_val"],
        text=sub_valid["partner_name"],
        customdata=np.stack([sub_valid["partner_code"], sub_valid["value_eur"], sub_valid["market_share_pct"]], axis=-1),
        hovertemplate="<b>%{text} (%{customdata[0]})</b><br>Volume: €%{customdata[1]:,.0f}<br>Part: %{customdata[2]:.2f}%<extra></extra>",
        colorscale=[[0.0, "#EDE9FE"], [0.2, "#DDD6FE"], [0.4, "#A78BFA"], [0.65, "#6366F1"], [0.85, "#4338CA"], [1.0, "#1E1B4B"]],
        zmin=cmin, zmax=cmax,
        showscale=True
    ))
    
    # Selected partner highlight
    sel_iso3 = ISO2_TO_ISO3.get(selected_partner)
    if sel_iso3:
        fig.add_trace(go.Choropleth(
            locations=[sel_iso3],
            z=[cmax],
            colorscale=[[0.0, STATEC_YELLOW], [1.0, STATEC_YELLOW]],
            showscale=False,
            hoverinfo="skip",
            marker_line_color=STATEC_YELLOW,
            marker_line_width=3,
        ))
    apply_map_theme(fig, title=f"Partenaires Commerciaux ({year})", height=420)
    print("Map figure created successfully!")

# Test building treemap
def test_treemap():
    df8 = load_drilldown_lvl8()
    sub = df8[(df8["partner_code"] == "DE") & (df8["flow"] == "IMPORT")].copy()
    sub = sub.sort_values("value_eur", ascending=False).head(20)
    sub["label"] = sub["product_code"].astype(str) + " - " + sub["product_name"].apply(lambda s: s[:30] + ".." if len(str(s)) > 30 else str(s))
    
    fig = px.treemap(
        sub,
        path=["label"],
        values="value_eur",
        color="value_eur",
        color_continuous_scale="Blues"
    )
    apply_plot_theme(fig, title="Panier de Produits (CN8)")
    print("Treemap created successfully!")

test_map()
test_treemap()
print("All figure tests passed!")
