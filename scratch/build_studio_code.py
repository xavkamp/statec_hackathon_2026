# Test studio code generation
import sys
sys.path.insert(0, '.')
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc

from src.dashboard.data_loader import (
    load_partner_rankings,
    load_product_rankings,
    load_product_partners,
    load_hs4_product_rankings,
    load_drilldown_lvl2,
    load_drilldown_lvl4,
    load_drilldown_lvl8,
)

print("Imports successful!")
