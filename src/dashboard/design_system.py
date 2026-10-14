"""Design System tokens and Plotly figure helpers for STATEC Hackathon 2026.
Follows clean modern typography and accessible color palettes.
"""

# Palette
PRIMARY = "#0284C7"       # Sky-600 — Primary brand / Exports
SECONDARY = "#4F46E5"     # Indigo-600 — Imports
SUCCESS = "#10B981"       # Emerald-500 — Surplus / Growth
DANGER = "#EF4444"        # Red-500 — Deficit / Decline
WARNING = "#F59E0B"       # Amber-500 — Caution / Secondary
NEUTRAL = "#64748B"       # Slate-500 — Axis labels, captions
SURFACE = "#FFFFFF"       # White card background
BACKGROUND = "#F8FAFC"    # Slate-50 app background
BORDER = "#E2E8F0"        # Slate-200 card borders
TEXT_PRIMARY = "#0F172A"  # Slate-900
TEXT_MUTED = "#64748B"    # Slate-500

# Categorical sequence (Colorblind-safe)
CATEGORICAL = [
    "#0284C7", "#4F46E5", "#10B981", "#F59E0B", "#EC4899",
    "#8B5CF6", "#14B8A6", "#F97316", "#6366F1", "#84CC16"
]

# Standard ISO-2 (Alpha-2) to ISO-3 (Alpha-3) country codes for Plotly choropleth rendering
ISO2_TO_ISO3 = {
    'AD': 'AND', 'AE': 'ARE', 'AF': 'AFG', 'AG': 'ATG', 'AI': 'AIA', 'AL': 'ALB', 'AM': 'ARM',
    'AO': 'AGO', 'AQ': 'ATA', 'AR': 'ARG', 'AS': 'ASM', 'AT': 'AUT', 'AU': 'AUS', 'AW': 'ABW',
    'AX': 'ALA', 'AZ': 'AZE', 'BA': 'BIH', 'BB': 'BRB', 'BD': 'BGD', 'BE': 'BEL', 'BF': 'BFA',
    'BG': 'BGR', 'BH': 'BHR', 'BI': 'BDI', 'BJ': 'BEN', 'BL': 'BLM', 'BM': 'BMU', 'BN': 'BRN',
    'BO': 'BOL', 'BQ': 'BES', 'BR': 'BRA', 'BS': 'BHS', 'BT': 'BTN', 'BV': 'BVT', 'BW': 'BWA',
    'BY': 'BLR', 'BZ': 'BLZ', 'CA': 'CAN', 'CC': 'CCK', 'CD': 'COD', 'CF': 'CAF', 'CG': 'COG',
    'CH': 'CHE', 'CI': 'CIV', 'CK': 'COK', 'CL': 'CHL', 'CM': 'CMR', 'CN': 'CHN', 'CO': 'COL',
    'CR': 'CRI', 'CU': 'CUB', 'CV': 'CPV', 'CW': 'CUW', 'CX': 'CXR', 'CY': 'CYP', 'CZ': 'CZE',
    'DE': 'DEU', 'DJ': 'DJI', 'DK': 'DNK', 'DM': 'DMA', 'DO': 'DOM', 'DZ': 'DZA', 'EC': 'ECU',
    'EE': 'EST', 'EG': 'EGY', 'EH': 'ESH', 'ER': 'ERI', 'ES': 'ESP', 'ET': 'ETH', 'FI': 'FIN',
    'FJ': 'FJI', 'FK': 'FLK', 'FM': 'FSM', 'FO': 'FRO', 'FR': 'FRA', 'GA': 'GAB', 'GB': 'GBR',
    'GD': 'GRD', 'GE': 'GEO', 'GF': 'GUF', 'GG': 'GGY', 'GH': 'GHA', 'GI': 'GIB', 'GL': 'GRL',
    'GM': 'GMB', 'GN': 'GIN', 'GP': 'GLP', 'GQ': 'GNQ', 'GR': 'GRC', 'GS': 'SGS', 'GT': 'GTM',
    'GU': 'GUM', 'GW': 'GNB', 'GY': 'GUY', 'HK': 'HKG', 'HM': 'HMD', 'HN': 'HND', 'HR': 'HRV',
    'HT': 'HTI', 'HU': 'HUN', 'ID': 'IDN', 'IE': 'IRL', 'IL': 'ISR', 'IM': 'IMN', 'IN': 'IND',
    'IO': 'IOT', 'IQ': 'IRQ', 'IR': 'IRN', 'IS': 'ISL', 'IT': 'ITA', 'JE': 'JEY', 'JM': 'JAM',
    'JO': 'JOR', 'JP': 'JPN', 'KE': 'KEN', 'KG': 'KGZ', 'KH': 'KHM', 'KI': 'KIR', 'KM': 'COM',
    'KN': 'KNA', 'KP': 'PRK', 'KR': 'KOR', 'KW': 'KWT', 'KY': 'CYM', 'KZ': 'KAZ', 'LA': 'LAO',
    'LB': 'LBN', 'LC': 'LCA', 'LI': 'LIE', 'LK': 'LKA', 'LR': 'LBR', 'LS': 'LSO', 'LT': 'LTU',
    'LU': 'LUX', 'LV': 'LVA', 'LY': 'LBY', 'MA': 'MAR', 'MC': 'MCO', 'MD': 'MDA', 'ME': 'MNE',
    'MF': 'MAF', 'MG': 'MDG', 'MH': 'MHL', 'MK': 'MKD', 'ML': 'MLI', 'MM': 'MMR', 'MN': 'MNG',
    'MO': 'MAC', 'MP': 'MNP', 'MQ': 'MTQ', 'MR': 'MRT', 'MS': 'MSR', 'MT': 'MLT', 'MU': 'MUS',
    'MV': 'MDV', 'MW': 'MWI', 'MX': 'MEX', 'MY': 'MYS', 'MZ': 'MOZ', 'NA': 'NAM', 'NC': 'NCL',
    'NE': 'NER', 'NF': 'NFK', 'NG': 'NGA', 'NI': 'NIC', 'NL': 'NLD', 'NO': 'NOR', 'NP': 'NPL',
    'NR': 'NRU', 'NU': 'NIU', 'NZ': 'NZL', 'OM': 'OMN', 'PA': 'PAN', 'PE': 'PER', 'PF': 'PYF',
    'PG': 'PNG', 'PH': 'PHL', 'PK': 'PAK', 'PL': 'POL', 'PM': 'SPM', 'PN': 'PCN', 'PR': 'PRI',
    'PS': 'PSE', 'PT': 'PRT', 'PW': 'PLW', 'PY': 'PRY', 'QA': 'QAT', 'RE': 'REU', 'RO': 'ROU',
    'RS': 'SRB', 'RU': 'RUS', 'RW': 'RWA', 'SA': 'SAU', 'SB': 'SLB', 'SC': 'SYC', 'SD': 'SDN',
    'SE': 'SWE', 'SG': 'SGP', 'SH': 'SHN', 'SI': 'SVN', 'SJ': 'SJM', 'SK': 'SVK', 'SL': 'SLE',
    'SM': 'SMR', 'SN': 'SEN', 'SO': 'SOM', 'SR': 'SUR', 'SS': 'SSD', 'ST': 'STP', 'SV': 'SLV',
    'SX': 'SXM', 'SY': 'SYR', 'SZ': 'SWZ', 'TC': 'TCA', 'TD': 'TCD', 'TF': 'ATF', 'TG': 'TGO',
    'TH': 'THA', 'TJ': 'TJK', 'TK': 'TKL', 'TL': 'TLS', 'TM': 'TKM', 'TN': 'TUN', 'TO': 'TON',
    'TR': 'TUR', 'TT': 'TTO', 'TV': 'TUV', 'TW': 'TWN', 'TZ': 'TZA', 'UA': 'UKR', 'UG': 'UGA',
    'UM': 'UMI', 'US': 'USA', 'UY': 'URY', 'UZ': 'UZB', 'VA': 'VAT', 'VC': 'VCT', 'VE': 'VEN',
    'VG': 'VGB', 'VI': 'VIR', 'VN': 'VNM', 'VU': 'VUT', 'WF': 'WLF', 'WS': 'WSM', 'YE': 'YEM',
    'YT': 'MYT', 'ZA': 'ZAF', 'ZM': 'ZMB', 'ZW': 'ZWE',
    # Eurostat / Comext aliases
    'UK': 'GBR', 'EL': 'GRC', 'XK': 'XKX', 'AN': 'ANT', 'CS': 'SCG', 'YU': 'YUG'
}

def add_iso3_column(df, col='partner_code'):
    """Adds 'iso3' column mapped from ISO-2 country codes for Plotly choropleth rendering."""
    if df is None:
        return None
    df = df.copy()
    if col in df.columns:
        df['iso3'] = df[col].map(ISO2_TO_ISO3)
    else:
        df['iso3'] = None
    return df


# Base Layout Dictionary (does not define xaxis/yaxis to prevent duplicate keyword conflicts)
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color=TEXT_PRIMARY, size=12),
    margin=dict(l=40, r=30, t=50, b=40),
    hoverlabel=dict(
        bgcolor="#1E293B",
        font_size=12,
        font_color="#F8FAFC",
        font_family="Inter, sans-serif"
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(color=NEUTRAL, size=11)
    )
)

def apply_plot_theme(fig, title=None, x_title=None, y_title=None, hovermode=None, dtick_x=None, autorange_y=None):
    """Apply consistent styling across all Plotly figures without duplicate keyword argument collisions."""
    layout_update = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color=TEXT_PRIMARY, size=12),
        margin=dict(l=40, r=30, t=50, b=40),
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=12,
            font_color="#F8FAFC",
            font_family="Inter, sans-serif"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=NEUTRAL, size=11)
        )
    )
    if title:
        layout_update["title"] = dict(text=f"<b>{title}</b>", font=dict(size=14, color=TEXT_PRIMARY))
    if hovermode:
        layout_update["hovermode"] = hovermode

    fig.update_layout(**layout_update)

    xaxis_update = dict(
        gridcolor="#F1F5F9",
        zerolinecolor="#E2E8F0",
        tickfont=dict(color=NEUTRAL, size=11),
    )
    if x_title:
        xaxis_update["title"] = dict(text=x_title, font=dict(color=TEXT_PRIMARY, size=12, weight="bold"))
    if dtick_x:
        xaxis_update["tickmode"] = "linear"
        xaxis_update["dtick"] = dtick_x
    fig.update_xaxes(**xaxis_update)

    yaxis_update = dict(
        gridcolor="#F1F5F9",
        zerolinecolor="#E2E8F0",
        tickfont=dict(color=NEUTRAL, size=11),
    )
    if y_title:
        yaxis_update["title"] = dict(text=y_title, font=dict(color=TEXT_PRIMARY, size=12, weight="bold"))
    if autorange_y:
        yaxis_update["autorange"] = autorange_y
    fig.update_yaxes(**yaxis_update)

    return fig

# Custom CSS styling dictionary
CARD_STYLE = {
    "backgroundColor": SURFACE,
    "borderRadius": "12px",
    "border": f"1px solid {BORDER}",
    "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)",
    "padding": "20px",
    "marginBottom": "20px"
}

KPI_CARD_STYLE = {
    "backgroundColor": SURFACE,
    "borderRadius": "12px",
    "border": f"1px solid {BORDER}",
    "boxShadow": "0 2px 4px 0 rgba(0, 0, 0, 0.04)",
    "padding": "18px 22px",
    "height": "100%"
}
