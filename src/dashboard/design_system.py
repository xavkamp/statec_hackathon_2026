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

# Custom CSS styling dictionary adhering to modern executive design standards
CARD_STYLE = {
    "backgroundColor": SURFACE,
    "borderRadius": "10px",
    "border": f"1px solid {BORDER}",
    "boxShadow": "0 2px 8px rgba(0, 26, 56, 0.04)",
    "padding": "22px",
    "marginBottom": "20px"
}

KPI_CARD_STYLE = {
    "backgroundColor": SURFACE,
    "borderRadius": "10px",
    "border": f"1px solid {BORDER}",
    "borderTop": f"4px solid {STATEC_NAVY}",
    "boxShadow": "0 2px 8px rgba(0, 26, 56, 0.05)",
    "padding": "20px 22px",
    "height": "100%"
}

STATEC_HEADING_STYLE = {
    "fontFamily": "'Montserrat', sans-serif",
    "fontWeight": "800",
    "textTransform": "uppercase",
    "letterSpacing": "1.2px",
    "color": STATEC_NAVY
}


def apply_map_theme(fig, scope="europe"):
    """Applies modern, high-contrast, institutional styling to Plotly Choropleth/Scattergeo maps."""
    fig.update_geos(
        showcoastlines=True, coastlinecolor="#CBD5E1",
        showland=True, landcolor="#EDF2F7",
        showocean=True, oceancolor="#F8FAFC",
        showcountries=True, countrycolor="#CBD5E1",
        showlakes=True, lakecolor="#F8FAFC",
        scope=scope if scope else "europe",
        projection_type="natural earth" if scope == "world" else "mercator",
        bgcolor="rgba(0,0,0,0)",
        framewidth=0
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family="'Inter', sans-serif", color=TEXT_PRIMARY)
    )
    return fig


from dash import html

def create_icon_badge(icon_class: str, color: str = STATEC_NAVY, bg: str = None, size: int = 15, box_size: int = 34):
    """
    Renders a modern, professional vector icon badge with soft background.
    Uses Bootstrap Icons (e.g. 'bi bi-shield-check', 'bi bi-box-arrow-up-right').
    """
    if bg is None:
        bg = "rgba(0, 26, 56, 0.05)"
    return html.Div(
        html.I(className=icon_class, style={"fontSize": f"{size}px", "color": color, "lineHeight": "1"}),
        style={
            "width": f"{box_size}px",
            "height": f"{box_size}px",
            "borderRadius": "8px",
            "backgroundColor": bg,
            "display": "inline-flex",
            "alignItems": "center",
            "justifyContent": "center",
            "flexShrink": "0",
            "border": "1px solid rgba(0, 0, 0, 0.04)"
        }
    )



INFO_HOVER_CSS = """
/* Interactive Hover Infobox Popovers */
.info-hover-wrapper {
    position: relative;
    display: inline-flex;
    align-items: center;
    vertical-align: middle;
}

.info-hover-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background-color: #EDF2F7;
    color: #001A38;
    font-size: 12px;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    border: 1.5px solid #CBD5E1;
    margin-left: 8px;
    line-height: 1;
    user-select: none;
}

.info-hover-wrapper:hover .info-hover-icon,
.info-hover-icon:hover {
    background-color: #FFC800 !important;
    color: #001A38 !important;
    border-color: #D9A700 !important;
    transform: scale(1.15);
    box-shadow: 0 2px 8px rgba(255, 200, 0, 0.45);
}

.info-hover-card {
    visibility: hidden;
    opacity: 0;
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    width: 450px;
    max-width: 88vw;
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-left: 4px solid #FFC800;
    border-radius: 8px;
    box-shadow: 0 14px 32px rgba(0, 26, 56, 0.22), 0 4px 12px rgba(0, 26, 56, 0.1);
    padding: 14px 16px;
    z-index: 999999;
    transition: opacity 0.2s cubic-bezier(0.16, 1, 0.3, 1), transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), visibility 0.2s;
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
.info-hover-card:hover {
    visibility: visible;
    opacity: 1;
    transform: translateY(0);
    pointer-events: auto;
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

.info-hover-text {
    text-decoration: underline dotted #0066B2 1.5px;
    text-underline-offset: 3px;
    cursor: help;
    display: inline-flex;
    align-items: center;
    position: relative;
    color: inherit;
    font-weight: 600;
}
.info-hover-text:hover {
    color: #0066B2;
}
"""

from dash import html

def create_info_hover(
    title: str,
    text_or_elements,
    icon: str = "ⓘ",
    variant: str = "gold",
    label_text: str = None,
    align: str = "left",
    className: str = ""
):
    """
    Renders an interactive hover element (info icon or text passage) that reveals
    a floating, formatted infobox tooltip when hovered.
    """
    configs = {
        "primary": {
            "border": STATEC_BLUE,
            "title_color": STATEC_NAVY,
            "icon_bg": "#EBF5FF",
            "icon_color": STATEC_BLUE,
            "border_color": STATEC_BLUE
        },
        "gold": {
            "border": STATEC_YELLOW,
            "title_color": STATEC_NAVY,
            "icon_bg": "#FFFBEB",
            "icon_color": "#B45309",
            "border_color": "#F59E0B"
        },
        "danger": {
            "border": STATEC_RED,
            "title_color": "#991B1B",
            "icon_bg": "#FEF2F2",
            "icon_color": STATEC_RED,
            "border_color": STATEC_RED
        },
        "navy": {
            "border": STATEC_NAVY,
            "title_color": STATEC_NAVY,
            "icon_bg": "#F1F5F9",
            "icon_color": STATEC_NAVY,
            "border_color": "#94A3B8"
        },
        "success": {
            "border": "#059669",
            "title_color": "#065F46",
            "icon_bg": "#ECFDF5",
            "icon_color": "#059669",
            "border_color": "#10B981"
        }
    }
    cfg = configs.get(variant, configs["gold"])

    content = text_or_elements if isinstance(text_or_elements, (list, tuple)) else [
        html.P(text_or_elements, style={"fontSize": "12px", "color": STATEC_GRAY, "margin": "0", "lineHeight": "1.5"})
    ]

    card = html.Div([
        html.Div([
            html.I(className="bi bi-info-circle-fill", style={"fontSize": "13px", "color": cfg["border"], "marginRight": "8px"}),
            html.Span(title.upper(), style={
                "fontFamily": "'Montserrat', sans-serif",
                "fontWeight": "800",
                "fontSize": "11px",
                "letterSpacing": "0.6px",
                "color": cfg["title_color"]
            }),
        ], className="d-flex align-items-center mb-1"),
        html.Div(content, style={"paddingLeft": "23px"})
    ], className="info-hover-card", style={"borderLeft": f"4px solid {cfg['border']}"})

    icon_node = html.I(className="bi bi-info-lg", style={"fontSize": "11px", "fontWeight": "800"}) if (icon == "ⓘ" or not icon) else (
        html.I(className=icon, style={"fontSize": "11px"}) if (isinstance(icon, str) and icon.startswith("bi ")) else icon
    )

    if label_text:
        trigger = html.Span([
            html.Span(label_text, style={"marginRight": "4px"}),
            html.Span(icon_node, className="info-hover-icon", style={
                "backgroundColor": cfg["icon_bg"], "color": cfg["icon_color"], "borderColor": cfg["border_color"]
            })
        ], className="info-hover-text")
    else:
        trigger = html.Span(
            icon_node,
            className="info-hover-icon",
            title="Hover to view explanation",
            style={
                "backgroundColor": cfg["icon_bg"],
                "color": cfg["icon_color"],
                "borderColor": cfg["border_color"]
            }
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
    info_icon: str = "ⓘ",
    info_variant: str = "gold",
    info_align: str = "left"
):
    """
    Generates a portal section heading with Montserrat bold typography, gold accent mark,
    and optional interactive hover infobox.
    """
    badge_elem = None
    if badge_text:
        badge_bg = badge_color if badge_color else STATEC_YELLOW
        badge_text_color = STATEC_NAVY if badge_bg == STATEC_YELLOW else "#FFFFFF"
        badge_elem = html.Span(
            badge_text,
            style={
                "backgroundColor": badge_bg,
                "color": badge_text_color,
                "fontFamily": "'Montserrat', sans-serif",
                "fontWeight": "800",
                "fontSize": "10.5px",
                "padding": "3px 9px",
                "borderRadius": "4px",
                "marginLeft": "12px",
                "letterSpacing": "0.5px",
                "textTransform": "uppercase"
            }
        )

    info_elem = None
    if info_content:
        info_elem = create_info_hover(
            title=info_title or title,
            text_or_elements=info_content,
            icon=info_icon,
            variant=info_variant,
            align=info_align
        )

    title_row = html.Div([
        html.H4(title, style={
            "fontFamily": "'Montserrat', sans-serif",
            "fontWeight": "800",
            "color": STATEC_NAVY,
            "margin": "0",
            "letterSpacing": "0.4px"
        }),
        badge_elem,
        info_elem
    ], className="d-flex align-items-center mb-1 flex-wrap")

    sub_elem = None
    if subtitle:
        sub_elem = html.P(
            subtitle,
            className="text-muted",
            style={"fontSize": "12.5px", "margin": "0 0 10px 0", "lineHeight": "1.45"}
        )

    return html.Div([
        title_row,
        html.Div(style={
            "width": "42px",
            "height": "4px",
            "backgroundColor": STATEC_YELLOW,
            "borderRadius": "2px",
            "marginBottom": "10px" if subtitle else "16px"
        }),
        sub_elem
    ], className="mb-3")


def create_infobox(title: str, text_or_elements, icon: str = "💡", variant: str = "primary", className: str = "mb-3"):
    """
    Renders a concise styled infobox for key metric explanations.
    Variants: 'primary' (Ministerial Blue), 'gold' (STATEC Yellow), 'danger' (Lux Lion Red), 'navy' (STATEC Navy), 'success' (Emerald).
    """
    configs = {
        "primary": {
            "border": STATEC_BLUE,
            "bg": "#F0F7FF",
            "title_color": STATEC_NAVY,
            "badge_bg": "#DBEAFE",
            "badge_color": STATEC_BLUE
        },
        "gold": {
            "border": STATEC_YELLOW,
            "bg": "#FFFDF5",
            "title_color": STATEC_NAVY,
            "badge_bg": "#FEF3C7",
            "badge_color": "#92400E"
        },
        "danger": {
            "border": STATEC_RED,
            "bg": "#FEF2F2",
            "title_color": "#991B1B",
            "badge_bg": "#FEE2E2",
            "badge_color": "#991B1B"
        },
        "navy": {
            "border": STATEC_NAVY,
            "bg": "#F8FAFC",
            "title_color": STATEC_NAVY,
            "badge_bg": "#E2E8F0",
            "badge_color": STATEC_NAVY
        },
        "success": {
            "border": "#059669",
            "bg": "#F0FDF4",
            "title_color": "#065F46",
            "badge_bg": "#DCFCE7",
            "badge_color": "#065F46"
        }
    }
    cfg = configs.get(variant, configs["primary"])

    content = text_or_elements if isinstance(text_or_elements, (list, tuple)) else [
        html.P(text_or_elements, style={"fontSize": "12px", "color": STATEC_GRAY, "margin": "0", "lineHeight": "1.5"})
    ]

    return html.Div([
        html.Div([
            html.Span(icon, style={"fontSize": "15px", "marginRight": "8px"}),
            html.Span(title.upper(), style={
                "fontFamily": "'Montserrat', sans-serif",
                "fontWeight": "800",
                "fontSize": "11px",
                "letterSpacing": "0.6px",
                "color": cfg["title_color"]
            }),
        ], className="d-flex align-items-center mb-1"),
        html.Div(content, style={"paddingLeft": "23px"})
    ], className=f"p-2 px-3 rounded {className}", style={
        "backgroundColor": cfg["bg"],
        "border": f"1px solid {BORDER}",
        "borderLeft": f"4px solid {cfg['border']}",
        "boxShadow": "0 1px 4px rgba(0, 26, 56, 0.04)"
    })


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
        return html.Span(f"HHI {hhi:.0f} • High Concentration (>2500)", style={
            "backgroundColor": "#FEE2E2", "color": "#B91C1C", "padding": "4px 10px",
            "borderRadius": "20px", "fontWeight": "600", "fontSize": "11px", "border": "1px solid #FCA5A5"
        })
    elif hhi >= 1500:
        return html.Span(f"HHI {hhi:.0f} • Moderate Concentration (1500–2500)", style={
            "backgroundColor": "#FEF3C7", "color": "#B45309", "padding": "4px 10px",
            "borderRadius": "20px", "fontWeight": "600", "fontSize": "11px", "border": "1px solid #FCD34D"
        })
    else:
        return html.Span(f"HHI {hhi:.0f} • Low Concentration (<1500)", style={
            "backgroundColor": "#D1FAE5", "color": "#047857", "padding": "4px 10px",
            "borderRadius": "20px", "fontWeight": "600", "fontSize": "11px", "border": "1px solid #6EE7B7"
        })


def create_dashboard_footer():
    """Institutional footer with English disclaimer for Hackathon 2026."""
    return html.Footer([
        html.Div([
            html.Div([
                html.Span("TRADE", style={
                    "fontSize": "20px", "fontWeight": "900", "fontFamily": "'Montserrat', sans-serif",
                    "color": "#FFFFFF", "letterSpacing": "-0.5px"
                }),
                html.Span(".lu", style={
                    "fontSize": "20px", "fontWeight": "900", "fontFamily": "'Montserrat', sans-serif",
                    "color": STATEC_YELLOW
                }),
                html.Span("INDEPENDENT EXTERNAL TRADE OBSERVATORY", style={
                    "fontSize": "9px", "fontWeight": "700", "letterSpacing": "1.2px",
                    "color": "#94A3B8", "display": "block", "marginTop": "2px"
                }),
            ], className="mb-3 mb-md-0"),

            html.Div([
                html.Span("Data sources: Eurostat Comext [ds-045409] & STATEC Open Data (2000–2026)", style={
                    "fontSize": "11.5px", "color": "#CBD5E1", "display": "block"
                }),
                html.Span("Analytical Research Project • Hackathon 2026 (Unofficial Prototype)", style={
                    "fontSize": "10.5px", "color": "#94A3B8", "display": "block", "marginTop": "2px"
                }),
            ], className="text-md-end text-start"),
        ], className="d-flex flex-column flex-md-row justify-content-between align-items-md-center py-4", style={"maxWidth": "1540px", "margin": "0 auto", "padding": "0 15px"}),

        html.Div([
            html.P("Disclaimer: This dashboard is an exploratory analytical research prototype created for the STATEC Hackathon 2026. It is not an official website or product of STATEC or the Government of the Grand Duchy of Luxembourg.", style={
                "fontSize": "10.5px", "color": "#94A3B8", "margin": "0", "textAlign": "center", "padding": "12px 15px",
                "backgroundColor": "#001226", "lineHeight": "1.5"
            })
        ])
    ], style={"backgroundColor": STATEC_NAVY, "marginTop": "60px", "color": "#FFFFFF", "borderTop": f"3px solid {STATEC_YELLOW}"})


# Compatibility alias
create_statec_footer = create_dashboard_footer



