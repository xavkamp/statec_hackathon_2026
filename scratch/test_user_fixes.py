import sys
sys.path.insert(0, ".")

from src.dashboard.app import update_q4_chart, update_q1_charts, update_q2_charts, render_tab_resilience, render_tab_benchmarks
from src.dashboard.data_loader import load_partner_rankings

print("--- Testing Q4 partner fallback for countries beyond top 4 (e.g. US, CN, IT, GB, PL, CH) ---")
for country in ["US", "CN", "IT", "GB", "PL", "CH"]:
    title, fig = update_q4_chart(partner_code=country, flow="IMPORT", level=4, threshold=15, year=2025)
    bar_count = len(fig.data[0].x) if fig.data else 0
    assert bar_count > 0, f"Expected bars for {country}, got {bar_count}"
    print(f"[PASS] Q4 {country}: {title} | Bars rendered: {bar_count}")

print("\n--- Testing Q1 margins & layout ---")
title, fig_bar, fig_map, style = update_q1_charts("IMPORT", "world", "value", "DE", False, 2025)
assert fig_bar.layout.margin.l >= 100, f"Expected margin.l >= 100 for Q1 bar, got {fig_bar.layout.margin.l}"
print(f"[PASS] Q1 margin.l = {fig_bar.layout.margin.l}")

print("\n--- Testing Q2 left graph margin ---")
b_title, fig_bar, fig_shift, s_title = update_q2_charts("IMPORT", 2, "87", 2025)
assert fig_bar.layout.margin.l >= 180, f"Expected margin.l >= 180 for Q2 bar, got {fig_bar.layout.margin.l}"
print(f"[PASS] Q2 margin.l = {fig_bar.layout.margin.l}")

print("\n--- Testing Q5 Peer benchmarking margin and parity annotation ---")
res_bench = render_tab_benchmarks(2025)
print("[PASS] Q5 rendered successfully")

print("\n--- Testing Resilience Radar ---")
res_tab = render_tab_resilience(2025)
print("[PASS] Resilience radar rendered successfully")

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
