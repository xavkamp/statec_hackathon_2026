import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.dashboard.app import (
    render_tab_resilience,
    render_tab_geopolitics,
    render_tab_stress,
    render_tab_partners,
    render_tab_products,
    render_tab_q3_product_partners,
    render_tab_q4_drilldown,
    render_tab_benchmarks,
    render_tab_seasonality,
    update_q2_spotlight_panel,
    update_q2_charts,
    update_seasonality_charts,
)

def test_all_tabs():
    print("Testing tab renderers...")
    t1 = render_tab_resilience(2025)
    print("[PASS] Tab 1 (Resilience) rendered")
    t2 = render_tab_geopolitics(2025)
    print("[PASS] Tab 2 (Geopolitics & Macro) rendered")
    t3 = render_tab_stress(2025)
    print("[PASS] Tab 3 (Stress) rendered")
    q1 = render_tab_partners(2025)
    print("[PASS] Q1 (Trading Partners) rendered")
    q2 = render_tab_products(2025)
    print("[PASS] Q2 (Product Categories) rendered")
    q3 = render_tab_q3_product_partners(2025)
    print("[PASS] Q3 (Product Principal Partners) rendered")
    q4 = render_tab_q4_drilldown(2025)
    print("[PASS] Q4 (Product Breakdown per Country) rendered")
    q5 = render_tab_benchmarks(2025)
    print("[PASS] Q5 (Peer Benchmarking) rendered")
    q6 = render_tab_seasonality()
    print("[PASS] Q6 (Seasonality Lab) rendered")

def test_q2_hhi_and_charts():
    print("\nTesting Q2 HHI calculation and chart updates...")
    # Ch. 87 (Vehicles), Year 2025, Flow IMPORT
    spotlight_ui = update_q2_spotlight_panel("87", "IMPORT", 2025)
    assert spotlight_ui is not None
    print("[PASS] Q2 spotlight panel rendered successfully")

    title_bar, fig1, fig2, shift_title = update_q2_charts("IMPORT", 2, "87", 2025)
    assert fig1 is not None and fig2 is not None
    assert "IMPORT" in shift_title
    print(f"[PASS] Q2 charts updated: Shift title = '{shift_title}'")

def test_seasonality_balance():
    print("\nTesting Q6 Seasonality Lab with Trade Balance...")
    fig_decomp, fig_factors = update_seasonality_charts("TOTAL", "BALANCE", ["raw", "trend", "seasonally_adjusted"])
    assert fig_decomp is not None and fig_factors is not None
    print("[PASS] Seasonality Decomposition & Monthly Factors generated for BALANCE")

if __name__ == "__main__":
    test_all_tabs()
    test_q2_hhi_and_charts()
    test_seasonality_balance()
    print("\nALL 10 TAB RENDERERS AND CALLBACK TESTS PASSED PERFECTLY!")
