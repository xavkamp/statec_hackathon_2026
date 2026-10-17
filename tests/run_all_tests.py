# -*- coding: utf-8 -*-
"""Master Test Runner for STATEC Hackathon 2026.
Runs all pipeline, dashboard, basket filtering, and regression suites.
"""

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.test_dashboard import test_all_tabs, test_q2_hhi_and_charts, test_q5_cagr_badges, test_seasonality_balance_and_clean_factors
from tests.test_basket_filters import test_all as test_basket_filtering
from tests.test_year_range import test_year_range
from tests.test_partner_drilldown import test_partner_drilldowns
from tests.test_regressions import (
    test_q4_year_and_share, test_q2_granularity_changes_fig32,
    test_year_sensitive_figures, test_seasonality_year_and_sectors,
)


def run_all():
    start_time = time.time()
    print("=" * 70)
    print("STATEC HACKATHON 2026 — MASTER TEST SUITE")
    print("=" * 70)

    suites = [
        ("Dashboard & Active Tabs", [test_all_tabs, test_q2_hhi_and_charts, test_q5_cagr_badges, test_seasonality_balance_and_clean_factors]),
        ("Critical Basket Filters", [test_basket_filtering]),
        ("Dynamic Year Range & Labels", [test_year_range]),
        ("Partner Drill-down & Margins", [test_partner_drilldowns]),
        ("Reported-Bug Regressions", [test_q4_year_and_share, test_q2_granularity_changes_fig32,
                                      test_year_sensitive_figures, test_seasonality_year_and_sectors]),
    ]

    total_suites = len(suites)
    passed_suites = 0

    for name, test_fns in suites:
        print(f"\n>>> Running Suite: {name}")
        try:
            for fn in test_fns:
                fn()
            passed_suites += 1
            print(f">>> SUITE PASSED: {name}")
        except Exception as e:
            print(f">>> SUITE FAILED: {name} — Error: {e}")
            raise e

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed_suites}/{total_suites} SUITES PASSED ({elapsed:.2f}s)")
    print("=" * 70)


if __name__ == "__main__":
    run_all()
