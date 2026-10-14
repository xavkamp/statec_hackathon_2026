import requests
import pandas as pd
import urllib3
import time
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/ds-045409"

# Year ranges to loop over (chunked to avoid 413)
YEAR_RANGES = [(2000, 2012), (2013, 2026)]

def fetch_range(product_code, since, until):
    params = {
        "freq": "A",
        "reporter": "LU",
        "product": product_code,
        "indicators": "VALUE_IN_EUROS",
        "sinceTimePeriod": str(since),
        "untilTimePeriod": str(until),
    }
    r = requests.get(BASE, params=params, verify=False, timeout=300)
    r.raise_for_status()
    return r.json()

def jsonstat_to_df(js):
    dims = js["id"]
    sizes = js["size"]
    labels = {d: js["dimension"][d]["category"]["label"] for d in dims}
    codes = {d: list(js["dimension"][d]["category"]["index"].keys()) for d in dims}

    strides = [1] * len(sizes)
    for i in range(len(sizes) - 2, -1, -1):
        strides[i] = strides[i + 1] * sizes[i + 1]

    rows = []
    for flat_idx_str, value in js.get("value", {}).items():
        flat_idx = int(flat_idx_str)
        coords = []
        rem = flat_idx
        for s in strides:
            coords.append(rem // s)
            rem = rem % s

        row = {"value": value}
        for d, pos in zip(dims, coords):
            code = codes[d][pos]
            row[d] = code
            row[f"{d}_label"] = labels[d].get(code, code)
        rows.append(row)

    return pd.DataFrame(rows) if rows else pd.DataFrame()

HS2_CODES = [f"{i:02d}" for i in range(1, 100)]

all_data = []
for hs2 in HS2_CODES:
    for (since, until) in YEAR_RANGES:
        print(f"Fetching product={hs2}, {since}-{until} ...")
        try:
            js = fetch_range(hs2, since, until)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 413:
                print(f"  413 for {hs2} {since}-{until}, skipping")
            else:
                print(f"  HTTP error: {e}")
            continue
        except Exception as e:
            print(f"  failed: {e}")
            continue

        df = jsonstat_to_df(js)
        if not df.empty:
            df["product"] = hs2
            all_data.append(df)
        time.sleep(0.5)

df_all = pd.concat(all_data, ignore_index=True)

mask = df_all["partner"].str.len() > 2
mask |= df_all["partner"].isin(["EU", "EZ"])
df_filtered = df_all[mask].copy()

df_all.to_csv("comext_LU_hs2_all.csv", index=False)
df_filtered.to_csv("comext_LU_hs2_filtered.csv", index=False)

print(df_filtered.head())
print(f"Total rows: {len(df_filtered)}")