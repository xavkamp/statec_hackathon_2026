"""Design System tokens and Plotly figure helpers for STATEC Hackathon 2026.
Follows clean modern typography and accessible color palettes.
"""

# Official STATEC (statistiques.public.lu) Design Tokens
STATEC_NAVY = "#001A38"      # Official portal midnight navy (Headers, Navigation, Brand)
STATEC_YELLOW = "#FFC800"    # Official .lu gold/yellow (Active highlights, accents, badges)
STATEC_BLUE = "#0066B2"      # Official Luxembourg Ministerial Blue (Exports, primary charts)
STATEC_RED = "#EA152C"       # Official Luxembourg Lion Red (Deficits, critical alerts)
STATEC_GRAY = "#556987"      # Portal slate gray (Muted text, secondary captions)
STATEC_BG = "#F4F6F9"        # Official portal background canvas
STATEC_SURFACE = "#FFFFFF"   # White card background
STATEC_BORDER = "#E2E8F0"    # Subtle structural border

# Functional Palette
PRIMARY = STATEC_BLUE        # Primary data flow (Exports, main actions)
SECONDARY = STATEC_NAVY      # Secondary data flow (Imports, brand structure)
SUCCESS = "#059669"          # Surplus / Growth
DANGER = STATEC_RED          # Deficit / Risk / Single point of failure
WARNING = STATEC_YELLOW      # Caution / Highlight / Spotlight / Active state
NEUTRAL = STATEC_GRAY        # Axis labels, captions, grid marks
SURFACE = STATEC_SURFACE     # Card surface
BACKGROUND = STATEC_BG       # App background canvas
BORDER = STATEC_BORDER       # Slate card borders
TEXT_PRIMARY = STATEC_NAVY   # High-contrast official navy text
TEXT_MUTED = STATEC_GRAY     # Secondary text

# Categorical sequence (STATEC Harmonic Palette)
CATEGORICAL = [
    STATEC_BLUE, STATEC_NAVY, STATEC_YELLOW, STATEC_RED, "#059669",
    "#0EA5E9", "#6366F1", "#D97706", "#EC4899", "#84CC16"
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
    font=dict(family="'Montserrat', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color=TEXT_PRIMARY, size=12),
    margin=dict(l=40, r=30, t=50, b=40),
    hoverlabel=dict(
        bgcolor=STATEC_NAVY,
        font_size=12,
        font_color="#FFFFFF",
        font_family="'Montserrat', 'Inter', sans-serif"
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
    """Apply consistent styling across all Plotly figures matching STATEC visual guidelines."""
    layout_update = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Montserrat', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color=TEXT_PRIMARY, size=12),
        margin=dict(l=40, r=30, t=50, b=40),
        hoverlabel=dict(
            bgcolor=STATEC_NAVY,
            font_size=12,
            font_color="#FFFFFF",
            font_family="'Montserrat', 'Inter', sans-serif"
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
        layout_update["title"] = dict(
            text=f"<b>{title}</b>",
            font=dict(family="'Montserrat', sans-serif", size=13, color=TEXT_PRIMARY)
        )
    if hovermode:
        layout_update["hovermode"] = hovermode

    fig.update_layout(**layout_update)

    xaxis_update = dict(
        gridcolor="#E5E7EB",
        zerolinecolor="#D1D5DB",
        tickfont=dict(color=NEUTRAL, size=11, family="'Inter', sans-serif"),
    )
    if x_title:
        xaxis_update["title"] = dict(text=x_title, font=dict(color=TEXT_PRIMARY, size=12, weight="bold", family="'Montserrat', sans-serif"))
    if dtick_x:
        xaxis_update["tickmode"] = "linear"
        xaxis_update["dtick"] = dtick_x
    fig.update_xaxes(**xaxis_update)

    yaxis_update = dict(
        gridcolor="#E5E7EB",
        zerolinecolor="#D1D5DB",
        tickfont=dict(color=NEUTRAL, size=11, family="'Inter', sans-serif"),
    )
    if y_title:
        yaxis_update["title"] = dict(text=y_title, font=dict(color=TEXT_PRIMARY, size=12, weight="bold", family="'Montserrat', sans-serif"))
    if autorange_y:
        yaxis_update["autorange"] = autorange_y
    fig.update_yaxes(**yaxis_update)

    return fig

# Custom CSS styling dictionaries kept as empty dicts for backwards compatibility
CARD_STYLE = {}
KPI_CARD_STYLE = {}
STATEC_HEADING_STYLE = {}


LUXEMBOURG_GEO = {
    "lat": 49.8153,
    "lon": 6.1296
}


def apply_map_theme(fig, scope="europe", center=None):
    """Applies modern, high-contrast, institutional styling to Plotly Choropleth/Scattergeo maps,
    centered on Luxembourg (49.8153° N, 6.1296° E) by default.
    """
    scope = scope if scope else "europe"
    target_center = center if center is not None else LUXEMBOURG_GEO

    geo_config = dict(
        showcoastlines=True, coastlinecolor="#CBD5E1",
        showland=True, landcolor="#EDF2F7",
        showocean=True, oceancolor="#F8FAFC",
        showcountries=True, countrycolor="#CBD5E1",
        showlakes=True, lakecolor="#F8FAFC",
        scope=scope,
        bgcolor="rgba(0,0,0,0)",
        framewidth=0
    )

    if scope == "world":
        geo_config["projection_type"] = "natural earth"
        geo_config["projection_rotation"] = dict(lon=target_center.get("lon", LUXEMBOURG_GEO["lon"]))
    else:
        geo_config["projection_type"] = "mercator"
        geo_config["center"] = target_center

    fig.update_geos(**geo_config)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family="'Inter', sans-serif", color=TEXT_PRIMARY)
    )
    return fig


from dash import html

def create_icon_badge(icon_class: str, variant: str = None, color: str = None, bg: str = None, size: int = None, box_size: int = None):
    """
    Renders a modern, professional vector icon badge with soft background.
    Uses Bootstrap Icons (e.g. 'bi bi-shield-check', 'bi bi-box-arrow-up-right').
    """
    mod_cls = ""
    if variant:
        mod_cls = f"icon-badge-{variant}"
    elif box_size == 40 or size == 20:
        mod_cls = "icon-badge-header"
    elif bg == "#EFF6FF" or color == STATEC_BLUE:
        mod_cls = "icon-badge-blue"
    elif bg == "#FFF9E6" or color == STATEC_NAVY:
        mod_cls = "icon-badge-gold"
    elif bg == "#FEF3C7" or color == "#B45309":
        mod_cls = "icon-badge-amber"
    elif bg == "#DCFCE7" or color == "#065F46":
        mod_cls = "icon-badge-emerald"

    return html.Div(
        html.I(className=icon_class),
        className=f"icon-badge {mod_cls}".strip()
    )


INFO_HOVER_CSS = """
.info-hover-wrapper {
    position: relative;
    display: inline-flex;
    align-items: center;
    vertical-align: middle;
}

.info-hover-icon {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 24px !important;
    height: 24px !important;
    border-radius: 50% !important;
    background-color: #EFF6FF !important;
    color: #005EB8 !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    cursor: pointer !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    border: 1.5px solid #BFDBFE !important;
    margin-left: 8px !important;
    line-height: 1 !important;
    user-select: none !important;
    outline: none !important;
}

.info-hover-wrapper:hover .info-hover-icon,
.info-hover-wrapper:focus-within .info-hover-icon,
.info-hover-icon:hover,
.info-hover-icon:focus {
    background-color: #FFC800 !important;
    color: #001A38 !important;
    border-color: #D9A700 !important;
    transform: scale(1.12) !important;
    box-shadow: 0 3px 10px rgba(255, 200, 0, 0.45) !important;
}

.info-hover-card {
    visibility: hidden;
    opacity: 0;
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    width: 480px !important;
    max-width: 90vw !important;
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-left: 4px solid #005EB8 !important;
    border-radius: 8px !important;
    box-shadow: 0 16px 36px rgba(0, 26, 56, 0.18), 0 4px 12px rgba(0, 26, 56, 0.08) !important;
    padding: 16px 18px !important;
    z-index: 999999 !important;
    transition: opacity 0.2s cubic-bezier(0.16, 1, 0.3, 1), transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), visibility 0.2s !important;
    transform: translateY(6px);
    pointer-events: none;
    text-align: left;
    white-space: normal;
}

.info-hover-align-right .info-hover-card {
    left: auto;
    right: 0;
}

.info-hover-wrapper:hover .info-hover-card,
.info-hover-wrapper:focus-within .info-hover-card,
.info-hover-card:hover {
    visibility: visible !important;
    opacity: 1 !important;
    transform: translateY(0) !important;
    pointer-events: auto !important;
}

.info-hover-card::before {
    content: "";
    position: absolute;
    top: -6px;
    left: 18px;
    width: 10px;
    height: 10px;
    background: #FFFFFF;
    border-left: 1px solid #CBD5E1;
    border-top: 1px solid #CBD5E1;
    transform: rotate(45deg);
}

.info-hover-align-right .info-hover-card::before {
    left: auto;
    right: 18px;
}

.infobox-card-header {
    display: flex !important;
    align-items: center !important;
    padding-bottom: 8px !important;
    margin-bottom: 10px !important;
    border-bottom: 1px solid #F1F5F9 !important;
}

.infobox-header-icon {
    color: #005EB8 !important;
    font-size: 14px !important;
    margin-right: 8px !important;
}

.infobox-card-title {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 11.5px !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    color: #001A38 !important;
    line-height: 1.2 !important;
    margin-bottom: 0 !important;
}

.infobox-card-body {
    padding-left: 2px !important;
}

.infobox-intro-text {
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    color: #1E293B !important;
    line-height: 1.5 !important;
    margin-bottom: 10px !important;
}

.infobox-item-row {
    margin-bottom: 8px !important;
    padding-bottom: 8px !important;
    border-bottom: 1px dashed #F1F5F9 !important;
}

.infobox-item-row:last-child {
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
    border-bottom: none !important;
}

.infobox-item-term {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #0F172A !important;
}

.infobox-item-desc {
    font-family: 'Inter', sans-serif !important;
    font-size: 11.5px !important;
    font-weight: 400 !important;
    color: #475569 !important;
    line-height: 1.45 !important;
    margin-top: 2px !important;
}

.infobox-pill-badge {
    display: inline-block !important;
    padding: 2px 7px !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    border-radius: 4px !important;
    margin-right: 8px !important;
    letter-spacing: 0.02em !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
    vertical-align: middle !important;
}

.infobox-badge-blue {
    background-color: #EFF6FF !important;
    color: #1D4ED8 !important;
    border: 1px solid #BFDBFE !important;
}

.infobox-badge-green,
.infobox-badge-success {
    background-color: #DCFCE7 !important;
    color: #15803D !important;
    border: 1px solid #86EFAC !important;
}

.infobox-badge-yellow,
.infobox-badge-warning {
    background-color: #FEF9C3 !important;
    color: #A16207 !important;
    border: 1px solid #FDE047 !important;
}

.infobox-badge-red,
.infobox-badge-danger {
    background-color: #FEE2E2 !important;
    color: #B91C1C !important;
    border: 1px solid #FCA5A5 !important;
}

.infobox-badge-neutral {
    background-color: #F1F5F9 !important;
    color: #334155 !important;
    border: 1px solid #CBD5E1 !important;
}
"""


def create_infobox_item(badge_text: str, title: str, description: str, badge_variant: str = "blue") -> html.Div:
    """
    Renders a unified, structured infobox row with a styled badge, bold title, and description.
    """
    badge_cls = f"infobox-badge-{badge_variant}"
    return html.Div([
        html.Div([
            html.Span(badge_text, className=f"infobox-pill-badge {badge_cls}"),
            html.Span(title, className="infobox-item-term")
        ], className="d-flex align-items-center mb-1"),
        html.Div(description, className="infobox-item-desc ps-1")
    ], className="infobox-item-row")


def create_info_hover(
    title: str,
    text_or_elements,
    icon: str = None,
    variant: str = "primary",
    label_text: str = None,
    align: str = "left",
    className: str = "",
    card_className: str = ""
):
    """
    Renders an interactive hover element that reveals
    a floating, harmonized infobox tooltip when hovered.
    """
    content = text_or_elements if isinstance(text_or_elements, (list, tuple)) else [
        html.P(text_or_elements, className="infobox-intro-text mb-0")
    ]

    card = html.Div([
        html.Div([
            html.I(className="bi bi-info-circle-fill infobox-header-icon me-2"),
            html.Span(title.upper(), className="infobox-card-title"),
        ], className="infobox-card-header"),
        html.Div(content, className="infobox-card-body")
    ], className=f"info-hover-card {card_className}".strip())

    icon_node = html.I(className="bi bi-info-lg fw-bold")

    if label_text:
        trigger = html.Span([
            html.Span(label_text, className="me-1"),
            html.Span(icon_node, className="info-hover-icon")
        ], className="section-info-pill", tabIndex=0)
    else:
        trigger = html.Span(
            icon_node,
            className="info-hover-icon",
            title="Hover or focus to view explanation",
            tabIndex=0
        )

    align_class = "info-hover-align-right" if align == "right" else ""
    return html.Span([trigger, card], className=f"info-hover-wrapper {align_class} {className}".strip())


def create_section_header(
    title: str,
    subtitle: str = None,
    badge_text: str = None,
    badge_color: str = None,
    info_title: str = None,
    info_content = None,
    info_icon: str = None,
    info_variant: str = "primary",
    info_align: str = "left",
    info_label: str = None,
    info_card_class: str = ""
):
    """
    Generates a portal section heading with Montserrat bold typography, gold accent mark,
    and optional interactive hover infobox.
    """
    badge_elem = None
    if badge_text:
        badge_cls = "badge-navy" if badge_color == STATEC_NAVY else "badge-gold"
        badge_elem = html.Span(
            badge_text,
            className=f"section-badge {badge_cls}"
        )

    info_elem = None
    if info_content:
        info_elem = create_info_hover(
            title=info_title or title,
            text_or_elements=info_content,
            icon=info_icon,
            variant=info_variant,
            align=info_align,
            label_text=info_label,
            card_className=info_card_class
        )

    title_row = html.Div([
        html.H4(title, className="section-title"),
        badge_elem,
        info_elem
    ], className="d-flex align-items-center mb-1 flex-wrap")

    sub_elem = html.P(subtitle, className="section-subtitle") if subtitle else None

    return html.Div([
        title_row,
        html.Div(className="title-accent-bar"),
        sub_elem
    ], className="section-header-box")


def create_infobox(title: str, text_or_elements, icon: str = "💡", variant: str = "primary", className: str = "mb-3"):
    """
    Renders a concise styled infobox for key metric explanations.
    """
    content = text_or_elements if isinstance(text_or_elements, (list, tuple)) else [
        html.P(text_or_elements, className="text-muted-custom mb-0 small")
    ]

    return html.Div([
        html.Div([
            html.Span(icon, className="me-2"),
            html.Span(title.upper(), className="kpi-label mb-0"),
        ], className="d-flex align-items-center mb-1"),
        html.Div(content, className="ps-3")
    ], className=f"dash-card infobox-{variant} {className}")


import pandas as pd

def fmt_eur(val: float) -> str:
    """Format euro value in Billions, Millions, or Thousands."""
    if val is None or pd.isna(val):
        return "—"
    abs_v = abs(val)
    sign = "-" if val < 0 else ""
    if abs_v >= 1e9:
        return f"{sign}€{abs_v/1e9:.2f}B"
    elif abs_v >= 1e6:
        return f"{sign}€{abs_v/1e6:.1f}M"
    elif abs_v >= 1e3:
        return f"{sign}€{abs_v/1e3:.0f}k"
    else:
        return f"{sign}€{abs_v:,.0f}"


def fmt_pct(val: float) -> str:
    """Format percentage value."""
    if val is None or pd.isna(val):
        return "—"
    return f"{val:.1f}%"


def get_concentration_badge(hhi: float):
    """Return colored badge for Herfindahl-Hirschman Index (HHI) concentration."""
    if pd.isna(hhi) or hhi is None:
        return html.Span("N/A", className="badge bg-secondary")
    if hhi >= 2500:
        return html.Span(f"HHI {hhi:.0f} • High Concentration (>2500)", className="badge-concentration-high")
    elif hhi >= 1500:
        return html.Span(f"HHI {hhi:.0f} • Moderate Concentration (1500–2500)", className="badge-concentration-mid")
    else:
        return html.Span(f"HHI {hhi:.0f} • Low Concentration (<1500)", className="badge-concentration-low")


def create_dashboard_footer():
    """Institutional footer with English disclaimer for Hackathon 2026."""
    from src.config import START_YEAR, END_YEAR

    return html.Footer([
        html.Div([
            html.Div([
                html.Div([
                    html.Span("HACKATHON", className="footer-logo-title"),
                    html.Span("26", className="footer-logo-accent"),
                ], className="ms-2 d-inline-flex align-items-baseline"),
            ], className="d-flex align-items-center mb-3 mb-md-0"),

            html.Div([
                html.Span(f"Data sources: Eurostat Comext [ds-045409] & STATEC Open Data ({START_YEAR}–{END_YEAR})", className="footer-source-text"),
                html.Span("Analytical Research Platform • STATEC Hackathon 2026 (Institutional Prototype)", className="footer-proto-text"),
            ], className="text-md-end text-start"),
        ], className="d-flex flex-column flex-md-row justify-content-between align-items-md-center py-4 footer-inner"),

        html.Div([
            html.P("This dashboard is a prototype created for the STATEC Hackathon 2026.", className="app-disclaimer-bar")
        ], className="app-disclaimer-wrap")
    ], className="app-footer")


# Compatibility alias
create_statec_footer = create_dashboard_footer



