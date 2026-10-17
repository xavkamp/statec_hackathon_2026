"""Regression tests for reported dashboard bugs (year updates, share metric, granularity)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.dashboard.app import (
    update_q4_chart, update_q2_charts, update_q3_charts, update_seasonality_charts,
    render_tab_resilience, update_sea_product_options,
)


def test_q4_year_and_share():
    t10, f10 = update_q4_chart("DE", "IMPORT", 4, 15, "ALL", 2010, "value")
    t20, f20 = update_q4_chart("DE", "IMPORT", 4, 15, "ALL", 2020, "value")
    assert "IN 2010" in t10 and "IN 2020" in t20
    assert list(f10.data[0].x) != list(f20.data[0].x)
    _, fs = update_q4_chart("DE", "IMPORT", 4, 15, "ALL", 2020, "share")
    assert fs.layout.xaxis.title.text.startswith("Share")
    assert all(0 <= v <= 100 for v in fs.data[0].x)
    print("  [PASS] Fig 2.4 year + share metric")


def test_q2_granularity_changes_fig32():
    traces = {}
    for g in (2, 4, 8):
        _, _, fig, _ = update_q2_charts("IMPORT", g, "ALL", None, 2020, "value")
        traces[g] = [t.name for t in fig.data]
    assert traces[2] != traces[4] != traces[8]
    print("  [PASS] Fig 3.2 follows granularity")


def test_year_sensitive_figures():
    a = update_q3_charts("87", "IMPORT", 2005)
    b = update_q3_charts("87", "IMPORT", 2020)
    assert str(a[0]) != str(b[0])
    r1, r2 = str(render_tab_resilience(2005)), str(render_tab_resilience(2020))
    assert r1 != r2
    print("  [PASS] Tab 1 / Fig 3.4 follow year")


def test_seasonality_year_and_sectors():
    _, f1 = update_seasonality_charts("TOTAL", "IMPORT", ["raw"], 2005)
    _, f2 = update_seasonality_charts("TOTAL", "IMPORT", ["raw"], 2025)
    assert list(f1.data[0].y) != list(f2.data[0].y)
    opts, _ = update_sea_product_options("FOOD", "01")
    assert {o["value"] for o in opts} >= {"01", "02", "03", "04", "10", "16", "19", "22"}
    opts, _ = update_sea_product_options("VEHICLES", "87")
    assert {o["value"] for o in opts} >= {"87", "88"}
    print("  [PASS] Fig 5.2 follows year; basket sectors complete")


if __name__ == "__main__":
    test_q4_year_and_share()
    test_q2_granularity_changes_fig32()
    test_year_sensitive_figures()
    test_seasonality_year_and_sectors()
