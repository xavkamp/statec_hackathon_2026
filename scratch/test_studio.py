import sys
import os
import pandas as pd
import plotly.graph_objects as go
from src.dashboard.data_loader import (
    load_partner_rankings,
    load_product_rankings,
    load_product_partners,
    load_hs4_product_rankings,
    load_drilldown_lvl2,
    load_drilldown_lvl4,
    load_drilldown_lvl8
)

def test_partner_products():
    partners_df = load_product_partners()
    print("load_product_partners loaded, rows:", len(partners_df))
    
    # Test top partners in drilldown
    lvl8 = load_drilldown_lvl8()
    print("lvl8 loaded, rows:", len(lvl8))
    
    lvl4 = load_drilldown_lvl4()
    print("lvl4 loaded, rows:", len(lvl4))
    
    lvl2 = load_drilldown_lvl2()
    print("lvl2 loaded, rows:", len(lvl2))
    
    # Check fallback for an arbitrary country like CN or IT
    for country in ["DE", "FR", "BE", "US", "IT", "CN", "BR"]:
        sub = partners_df[(partners_df["partner_code"] == country) & (partners_df["flow"] == "IMPORT") & (partners_df["year"] == 2024)]
        print(f"Country {country} in 2024 IMPORT has {len(sub)} HS2 records, total val: {sub['value_eur'].sum():,.0f} €")

test_partner_products()
