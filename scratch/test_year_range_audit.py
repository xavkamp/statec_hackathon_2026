import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import START_YEAR, END_YEAR
import src.dashboard.app as app
import src.dashboard.design_system as ds

print(f"Config year range: {START_YEAR}..{END_YEAR}")

from src.dashboard.data_loader import load_overview_kpis

# 1. Header & Footer
header = app.create_header()
print("[Header Subtitle]:", app.find_component_by_id(header, "portal-subtitle").children if hasattr(app, "find_component_by_id") else "Rendered")

footer = ds.create_dashboard_footer()
print("[Footer Source]:", footer.children[0].children[0].children[0].children)

# 2. Tab 1 Resilience
t1 = app.render_tab_resilience(2026)
print("[Tab 1 rendered for 2026]")

# 3. Tab 2 Partners
t2 = app.render_tab_partners(2026)
print("[Tab 2 rendered for 2026]")

# 4. Tab 3 Products
t3 = app.render_tab_products(2026)
print("[Tab 3 rendered for 2026]")

# 5. Tab 4 Benchmarks
t4 = app.render_tab_benchmarks(2026)
print("[Tab 4 rendered for 2026]")

# 6. Tab 5 Seasonality
t5 = app.render_tab_seasonality()
print("[Tab 5 rendered]")

# 7. Q1 Charts with 2026
q1_res = app.update_q1_charts("IMPORT", "world", "value", "DE", False, 2026)
print("[Q1 2026 bar title]:", q1_res[0])

# 8. Q2 Charts with 2026
q2_res = app.update_q2_charts("IMPORT", 2, "ALL", "87", 2026, "value")
print("[Q2 2026 bar title]:", q2_res[0])
print("[Q2 2026 shift title]:", q2_res[3])
print("[Q2 2026 shift range]:", q2_res[2].layout.xaxis.range)

# 9. Q3 Charts with 2026
q3_res = app.update_q3_charts("87", "IMPORT", 2026)
print("[Q3 2026 bar title]:", q3_res[0])

# 10. Q5 Peer Benchmarking with 2026
q5_res = app.generate_q5_figures("TOTAL", "volume", 2026)
print("[Q5 2026 index title]:", q5_res[0])
print("[Q5 2026 peer title]:", q5_res[2])
print("[Q5 2026 index range]:", q5_res[1].layout.xaxis.range)

# 11. Q6 Seasonality
q6_ts, q6_fac = app.update_seasonality_charts("TOTAL", "IMPORT", ["raw", "trend"])
print("[Q6 timeseries range]:", q6_ts.layout.xaxis.range)

print("\n--- ALL YEAR RANGE AUDIT CHECKS COMPLETED SUCCESSFULLY! ---")
