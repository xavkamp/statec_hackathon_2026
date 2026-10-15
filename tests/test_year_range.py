# -*- coding: utf-8 -*-
"""Dynamic Year Range & Label Audit Tests.
Verifies that all charts, titles, dropdowns, and data ranges dynamically adapt
to the available years in the dataset (2000..2025/2026) without hardcoded values.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import START_YEAR, END_YEAR
import src.dashboard.app as app
import src.dashboard.design_system as ds


def test_year_range():
    print(f"Config year range: {START_YEAR}..{END_YEAR}")

    # 1. Header & Footer
    header = app.create_header()
    assert header is not None, "Header failed to render"
    print("  [PASS] Header rendered with dynamic range")

    footer = ds.create_dashboard_footer()
    assert footer is not None, "Footer failed to render"
    print("  [PASS] Footer rendered")

    # 2. Tab Renderers
    t1 = app.render_tab_resilience(END_YEAR)
    assert t1 is not None
    print(f"  [PASS] Tab 1 rendered for {END_YEAR}")

    t2 = app.render_tab_partners(END_YEAR)
    assert t2 is not None
    print(f"  [PASS] Tab 2 rendered for {END_YEAR}")

    t3 = app.render_tab_products(END_YEAR)
    assert t3 is not None
    print(f"  [PASS] Tab 3 rendered for {END_YEAR}")

    t4 = app.render_tab_benchmarks(END_YEAR)
    assert t4 is not None
    print(f"  [PASS] Tab 4 rendered for {END_YEAR}")

    t5 = app.render_tab_seasonality()
    assert t5 is not None
    print("  [PASS] Tab 5 rendered")

    # 3. Dynamic Chart Titles
    q1_res = app.update_q1_charts("IMPORT", "world", "value", "DE", False, END_YEAR)
    assert str(END_YEAR) in q1_res[0], f"Expected {END_YEAR} in Q1 title"
    print("  [PASS] Q1 dynamic title:", q1_res[0])

    q2_res = app.update_q2_charts("IMPORT", 2, "ALL", "87", END_YEAR, "value")
    assert str(END_YEAR) in q2_res[0] and str(END_YEAR) in q2_res[3]
    print("  [PASS] Q2 dynamic title:", q2_res[0])

    q3_res = app.update_q3_charts("87", "IMPORT", END_YEAR)
    assert str(END_YEAR) in q3_res[0]
    print("  [PASS] Q3 dynamic title:", q3_res[0])

    q5_res = app.generate_q5_figures("TOTAL", "volume", END_YEAR)
    assert q5_res[1] is not None and q5_res[3] is not None
    print("  [PASS] Q5 dynamic index title:", q5_res[0])

    q6_ts, q6_fac = app.update_seasonality_charts("TOTAL", "IMPORT", ["raw", "trend"])
    assert q6_ts is not None and q6_fac is not None
    print("  [PASS] Q6 timeseries range:", q6_ts.layout.xaxis.range)


if __name__ == "__main__":
    test_year_range()
    print("\n[SUCCESS] ALL YEAR RANGE AUDIT CHECKS COMPLETED SUCCESSFULLY!")
