import plotly.graph_objects as go
from pathlib import Path

f1 = go.Figure(go.Choropleth(locations=['LUX', 'USA', 'CHN', 'AUS', 'BRA'], z=[10, 5, 4, 3, 2]))
f1.update_geos(scope='world', projection_type='natural earth', center=dict(lat=49.8153, lon=6.1296))
f1.update_layout(title='Case 1: center=(49.8, 6.13)', height=350, margin=dict(l=0, r=0, t=35, b=0))

f2 = go.Figure(go.Choropleth(locations=['LUX', 'USA', 'CHN', 'AUS', 'BRA'], z=[10, 5, 4, 3, 2]))
f2.update_geos(scope='world', projection_type='natural earth', projection_rotation=dict(lon=6.1296), center=dict(lat=49.8153, lon=0))
f2.update_layout(title='Case 2: rot lon=6.13, center lat=49.8', height=350, margin=dict(l=0, r=0, t=35, b=0))

f3 = go.Figure(go.Choropleth(locations=['LUX', 'USA', 'CHN', 'AUS', 'BRA'], z=[10, 5, 4, 3, 2]))
f3.update_geos(scope='world', projection_type='natural earth', projection_rotation=dict(lon=6.1296))
f3.update_layout(title='Case 3: rot lon=6.13 (no lat shift)', height=350, margin=dict(l=0, r=0, t=35, b=0))

html = f"""
<html><head><script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script></head>
<body style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">
<div>{f1.to_html(full_html=False, include_plotlyjs=False)}</div>
<div>{f2.to_html(full_html=False, include_plotlyjs=False)}</div>
<div>{f3.to_html(full_html=False, include_plotlyjs=False)}</div>
</body></html>
"""
Path('scratch/test_world_centers.html').write_text(html, encoding='utf-8')
print('Written scratch/test_world_centers.html')
