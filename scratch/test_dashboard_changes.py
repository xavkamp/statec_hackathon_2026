import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.dashboard.app import (
    render_tab_resilience,
    render_tab_partners,
    render_tab_products,
    render_tab_benchmarks,
    render_tab_seasonality,
    update_q2_spotlight_panel,
    update_q2_charts,
    generate_q5_figures,
    update_q5_charts,
    update_seasonality_charts,
)

def test_all_tabs():
    print("Testing tab renderers...")
    t1 = render_tab_resilience(2025)
    assert t1 is not None
    print("[PASS] Tab 1 (Resilience Radar) rendered")

    q1_q4 = render_tab_partners(2025)
    assert q1_q4 is not None
    print("[PASS] Tab 2 (Trading Partners Q1 & Q4) rendered")

    q2_q3 = render_tab_products(2025)
    assert q2_q3 is not None
    print("[PASS] Tab 3 (Product Categories Q2 & Q3) rendered")

    q5 = render_tab_benchmarks(2025)
    assert q5 is not None
    print("[PASS] Tab 4 (Peer Benchmarking Q5) rendered")

    q6 = render_tab_seasonality()
    assert q6 is not None
    print("[PASS] Tab 5 (Seasonality Lab Q6) rendered")

def test_q2_hhi_and_charts():
    print("\nTesting Q2 HHI calculation and chart updates...")
    # Ch. 87 (Vehicles), Year 2025, Flow IMPORT
    spotlight_ui = update_q2_spotlight_panel("87", "IMPORT", 2025)
    assert spotlight_ui is not None
    print("[PASS] Q2 spotlight panel rendered successfully")

    # Volume mode
    title_bar, fig1, fig2, shift_title = update_q2_charts("IMPORT", 2, "ALL", "87", 2025, "value")
    assert fig1 is not None and fig2 is not None
    assert "STRUCTURAL TRANSFORMATION" in shift_title
    print(f"[PASS] Q2 charts updated (Volume mode): Shift title = '{shift_title}'")

    # Market share mode
    title_bar_s, fig1_s, fig2_s, shift_title_s = update_q2_charts("IMPORT", 2, "ALL", "87", 2025, "share")
    assert fig2_s is not None
    assert "MARKET SHARE EVOLUTION" in shift_title_s
    print(f"[PASS] Q2 charts updated (Share mode): Shift title = '{shift_title_s}'")

def test_q5_cagr_badges():
    print("\nTesting Q5 Peer Benchmarking with CAGR badges...")
    t_left, fig_idx, t_right, fig_right, cagr_badges = generate_q5_figures("TOTAL", "volume", 2025)
    assert fig_idx is not None and fig_right is not None
    assert cagr_badges is not None
    print(f"[PASS] Q5 CAGR badges generated: '{t_left}'")

def test_seasonality_balance_and_annotations():
    print("\nTesting Q6 Seasonality Lab with Trade Balance and Annotations...")
    fig_decomp, fig_factors = update_seasonality_charts("TOTAL", "BALANCE", ["raw", "trend", "seasonally_adjusted"])
    assert fig_decomp is not None and fig_factors is not None
    assert len(fig_factors.layout.annotations) > 0
    print("[PASS] Seasonality Decomposition & Monthly Factors generated for BALANCE with annotations")

    fig_ts_imp, fig_fact_imp = update_seasonality_charts("TOTAL", "IMPORT", ["raw", "trend"])
    assert fig_ts_imp is not None and fig_fact_imp is not None
    assert len(fig_fact_imp.layout.annotations) >= 2
    print(f"[PASS] Seasonality IMPORT factors generated with {len(fig_fact_imp.layout.annotations)} callout annotations")

if __name__ == "__main__":
    test_all_tabs()
    test_q2_hhi_and_charts()
    test_q5_cagr_badges()
    test_seasonality_balance_and_annotations()
    print("\nALL 5 ACTIVE TABS AND REGRESSION TESTS PASSED PERFECTLY!")
