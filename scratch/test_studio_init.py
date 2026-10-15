import sys
sys.path.insert(0, '.')
import pandas as pd
import numpy as np

# Test extracting code from string or list
def parse_code(c):
    if c is None:
        return "DE"
    res = c[0] if isinstance(c, (list, tuple, np.ndarray)) else str(c)
    return str(res).strip().upper()

print("String 'FR':", parse_code("FR"))
print("List ['FR', 123]:", parse_code(["FR", 123]))
print("Array np.array(['FR', '100']):", parse_code(np.array(["FR", "100"])))

y_label = "France (FR)"
print("Extracted from label:", y_label.split("(")[-1].split(")")[0].strip().upper())
