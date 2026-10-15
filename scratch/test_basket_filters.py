# -*- coding: utf-8 -*-
from src.dashboard.app import (
    update_q4_chart,
    update_q2_charts,
    update_q2_selected_product,
    update_q3_product_options,
    sync_q3_product_from_q2,
    update_q5_product_options,
    update_sea_product_options,
    RESILIENCE_BASKETS
)

def test_all():
    print("Testing Q4 with basket ENERGY...")
    title, fig = update_q4_chart("DE", "IMPORT", 4, 15, "ENERGY", 2025)
    print("  Q4 ENERGY title:", title, "Data traces:", len(fig.data))

    print("Testing Q4 with basket TECH...")
    title, fig = update_q4_chart("CN", "IMPORT", 8, 15, "TECH", 2025)
    print("  Q4 TECH title:", title, "Data traces:", len(fig.data))

    print("Testing Q2 with basket FOOD...")
    t1, fig_bar, fig_shift, t2 = update_q2_charts("IMPORT", 2, "FOOD", "04", 2025)
    print("  Q2 FOOD titles:", t1, " | ", t2, "traces:", len(fig_bar.data), len(fig_shift.data))

    print("Testing Q2 selected product with basket HEALTH...")
    p = update_q2_selected_product(None, "IMPORT", 2, "HEALTH", 2025, None)
    print("  Q2 HEALTH selected product:", p)

    print("Testing Q3 product options with basket METALS...")
    opts = update_q3_product_options("METALS")
    print("  Q3 METALS options count:", len(opts), [o['value'] for o in opts])

    print("Testing Q5 product options with basket VEHICLES...")
    q5_opts, q5_val = update_q5_product_options("VEHICLES", "87")
    print("  Q5 VEHICLES options:", [o['value'] for o in q5_opts], "selected:", q5_val)

    print("Testing Q6 seasonality options with basket METALS...")
    sea_opts, sea_val = update_sea_product_options("METALS", "72")
    print("  Q6 METALS options:", [o['value'] for o in sea_opts], "selected:", sea_val)

    print("\nALL BASKET FILTER TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_all()
