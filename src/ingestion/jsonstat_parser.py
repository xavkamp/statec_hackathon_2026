"""Parser for Eurostat JSON-stat 2.0 response format.
Converts multi-dimensional JSON-stat data into tidy pandas DataFrames.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


def jsonstat_to_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """Parse Eurostat JSON-stat dictionary into a tidy pandas DataFrame.
    
    Handles both sparse dictionary values and dense array values.
    Maps dimension indices to their codes and labels.
    """
    if not data or "dimension" not in data:
        return pd.DataFrame()

    dim_ids = data.get("id", [])
    sizes = data.get("size", [])
    dims = data.get("dimension", {})
    raw_values = data.get("value", {})

    if not dim_ids or not sizes:
        return pd.DataFrame()

    # Pre-calculate strides for row-major multidimensional indexing
    # stride[j] = prod(size[j+1:])
    strides = []
    current_stride = 1
    for s in reversed(sizes):
        strides.append(current_stride)
        current_stride *= s
    strides.reverse()

    # Build index to code & label mapping for each dimension
    dim_mappings = []
    for dim_id in dim_ids:
        dim_info = dims.get(dim_id, {})
        category = dim_info.get("category", {})
        idx_map = category.get("index", {})
        labels = category.get("label", {})

        # index can be a dict {code: pos} or a list [code1, code2, ...]
        if isinstance(idx_map, dict):
            pos_to_code = {v: k for k, v in idx_map.items()}
        elif isinstance(idx_map, list):
            pos_to_code = {i: code for i, code in enumerate(idx_map)}
        else:
            # Fallback to labels dict keys if index not present
            pos_to_code = {i: code for i, code in enumerate(labels.keys())}

        dim_mappings.append({
            "id": dim_id,
            "pos_to_code": pos_to_code,
            "labels": labels
        })

    # If raw_values is a dict { "index": val }, convert to rows
    rows = []
    if isinstance(raw_values, dict):
        for idx_str, val in raw_values.items():
            if val is None:
                continue
            idx = int(idx_str)
            # Decompose linear index into dimension positions
            temp = idx
            row = {}
            for j, dim_meta in enumerate(dim_mappings):
                stride = strides[j]
                pos = temp // stride
                temp = temp % stride
                code = dim_meta["pos_to_code"].get(pos, str(pos))
                label = dim_meta["labels"].get(code, code)
                row[dim_meta["id"]] = code
                row[f"{dim_meta['id']}_label"] = label
            row["value"] = float(val)
            rows.append(row)
    elif isinstance(raw_values, list):
        for idx, val in enumerate(raw_values):
            if val is None or pd.isna(val):
                continue
            temp = idx
            row = {}
            for j, dim_meta in enumerate(dim_mappings):
                stride = strides[j]
                pos = temp // stride
                temp = temp % stride
                code = dim_meta["pos_to_code"].get(pos, str(pos))
                label = dim_meta["labels"].get(code, code)
                row[dim_meta["id"]] = code
                row[f"{dim_meta['id']}_label"] = label
            row["value"] = float(val)
            rows.append(row)

    df = pd.DataFrame(rows)
    return df
