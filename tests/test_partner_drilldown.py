# -*- coding: utf-8 -*-
"""Partner Drill-Down & Geographic Scope Tests.
Verifies hierarchical tariff drill-down (HS2 -> HS4 -> CN8) and fallback mechanisms
for both major European neighbors and global trade partners.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dashboard.app import update_q4_chart, update_q1_charts, update_q2_charts


def test_partner_drilldowns():
    print("Testing partner drill-down fallback for global partners (US, CN, IT, GB, PL, CH)...")
    for country in ["US", "CN", "IT", "GB", "PL", "CH"]:
        title, fig = update_q4_chart(partner_code=country, flow="IMPORT", level=4, threshold=15, basket="ALL", year=2025)
        bar_count = len(fig.data[0].x) if fig.data else 0
        assert bar_count > 0, f"Expected bars for {country}, got {bar_count}"
        print(f"  [PASS] Q4 {country}: {title} | Bars rendered: {bar_count}")

    print("\nTesting Q1 margins & layout responsiveness...")
    title, fig_bar, fig_map, style = update_q1_charts("IMPORT", "world", "value", "DE", False, 2025)
    assert fig_bar.layout.margin.l >= 100, f"Expected margin.l >= 100 for Q1 bar, got {fig_bar.layout.margin.l}"
    print(f"  [PASS] Q1 margin.l = {fig_bar.layout.margin.l}")

    print("\nTesting Q2 left graph margin...")
    b_title, fig_bar, fig_shift, s_title = update_q2_charts("IMPORT", 2, "ALL", "87", 2025, "value")
    assert fig_bar.layout.margin.l >= 180, f"Expected margin.l >= 180 for Q2 bar, got {fig_bar.layout.margin.l}"
    print(f"  [PASS] Q2 margin.l = {fig_bar.layout.margin.l}")


if __name__ == "__main__":
    test_partner_drilldowns()
    print("\n[SUCCESS] ALL PARTNER DRILLDOWN & GEOGRAPHY TESTS PASSED SUCCESSFULLY!")
