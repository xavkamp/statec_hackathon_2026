# =============================================================================
# Radar de résilience : version Shiny adaptée au CSV Comext
# (annuel, chapitres HS2, importations et exportations, valeurs en euros)
# =============================================================================

library(shiny)
library(bslib)
library(bsicons)
library(data.table)
library(purrr)
library(ggplot2)
library(DT)
library(sf)

# 1. CONFIGURATION ------------------------------------------------------------

brandPalette <- c("#F39200", "#E71E73", "#951B81", "#E84E0F",
                  "#C3004D", "#662483", "#575783")

cfg <- list(
  dataPath = file.path("data", "resilienceData.rds"),
  lux      = "LU",
  hubs     = c("BE", "NL"),
  allBasket = "all",
  allExclude = "99",
  thresholds = c(moderate = 1500, concentrated = 2500),
  hhiMax   = 10000,
  topPartners = 6L,
  shiftCandidates = 8L,
  shiftShown = 6L,
  trend    = list(minYMax = 3000, yStep = 1000),
  stress   = list(yearsBefore = 3L, yearsAfter = 3L, postOffset = 1L),
  shareSteps = c(0.001, 0.01, 0.05, 0.10, 0.25, 0.50),
  defaults = list(mapView = "eu", basket = "energy", flow = "import"),
  luxPoint = c(lon = 6.13, lat = 49.61),
  
  flows = list(
    import = list(code = "1", label = "Importations", partners = "fournisseurs",
                  mapTitle = "D'où viennent les importations : %s"),
    export = list(code = "2", label = "Exportations", partners = "clients",
                  mapTitle = "Où vont les exportations : %s")
  ),
  
  euFrom = c(AT = 1995L, BE = 1995L, DE = 1995L, DK = 1995L, ES = 1995L,
             FI = 1995L, FR = 1995L, GB = 1995L, GR = 1995L, EL = 1995L,
             IE = 1995L, IT = 1995L, LU = 1995L, NL = 1995L, PT = 1995L,
             SE = 1995L,
             CY = 2004L, CZ = 2004L, EE = 2004L, HU = 2004L, LT = 2004L,
             LV = 2004L, MT = 2004L, PL = 2004L, SI = 2004L, SK = 2004L,
             BG = 2007L, RO = 2007L, HR = 2013L),
  euUntil = c(GB = 2019L),
  
  mapViews = list(
    eu    = list(label = "Europe", xlim = c(-12, 38), ylim = c(33, 67), crs = NULL),
    world = list(label = "Monde", xlim = c(-170, 180), ylim = c(-58, 84),
                 crs = "+proj=robin")
  ),
  colours = list(
    levels   = c(diversified = brandPalette[7], moderate = brandPalette[1],
                 concentrated = brandPalette[5], none = "#9A9A9A"),
    accent   = brandPalette[3],
    lux      = brandPalette[7],
    hub      = "#BDBDBD",
    noImport = "#EDEDED",
    positive = brandPalette[7],
    negative = brandPalette[5],
    seqRamp  = brandPalette[c(1, 2, 6)],
    flows    = c(import = brandPalette[1], export = brandPalette[3]),
    grey     = "#888888"
  ),
  
  baskets = list(
    energy = list(label = "Énergie", products = c(
      "27" = "Combustibles minéraux, huiles minérales (pétrole, gaz, houille)")),
    food = list(label = "Alimentation", products = c(
      "02" = "Viandes", "04" = "Produits laitiers, œufs, miel", "07" = "Légumes",
      "08" = "Fruits et fruits à coque", "10" = "Céréales",
      "15" = "Graisses et huiles", "31" = "Engrais")),
    health = list(label = "Santé et médicaments", products = c(
      "30" = "Produits pharmaceutiques",
      "90" = "Instruments d'optique, de mesure et médicaux")),
    raw = list(label = "Matières premières", products = c(
      "26" = "Minerais", "39" = "Matières plastiques", "40" = "Caoutchouc",
      "72" = "Fonte, fer et acier", "74" = "Cuivre", "76" = "Aluminium")),
    tech = list(label = "Technologies", products = c(
      "84" = "Machines et appareils mécaniques (dont ordinateurs)",
      "85" = "Appareils électriques (téléphones, semi-conducteurs, batteries)")),
    all = list(label = "Ensemble des biens", products = character())
  ),
  
  events = list(
    dotcom  = list(label = "Bulle internet 2001", year = 2001L,
                   note = "Éclatement de la bulle technologique et ralentissement mondial en 2001."),
    enlarge = list(label = "Élargissement UE 2004", year = 2004L,
                   note = "Adhésion de dix pays à l'UE le 1er mai 2004 : change le périmètre « UE » et les circuits d'approvisionnement."),
    gfc     = list(label = "Crise financière 2008", year = 2008L,
                   note = "Faillite de Lehman Brothers en septembre 2008 ; fort recul du commerce mondial en 2009."),
    debt    = list(label = "Crise de la dette 2011", year = 2011L,
                   note = "Crise des dettes souveraines dans la zone euro."),
    covid   = list(label = "COVID 2020", year = 2020L,
                   note = "Premiers confinements en Europe à partir de mars 2020."),
    gas     = list(label = "Crise du gaz 2022", year = 2022L,
                   note = "Invasion de l'Ukraine en février 2022 ; flambée des prix de l'énergie.")
  ),
  
  labels = list(
    appTitle  = "Radar de résilience",
    eyebrow   = "STATEC Hackathon 2026 · Stratégie nationale de résilience, piliers 3–5",
    subtitle  = "De qui le Luxembourg dépend-il, et à qui vend-il ? Concentration des partenaires commerciaux, par panier, produit et pays.",
    lastYear = "Dernière année", release = "Fichier du",
    flow = "Flux", year = "Année", mapView = "Vue de la carte",
    hubsToggle = "Voir à travers les hubs BE/NL (les exclure des parts)",
    gaugeTitle = "Résister · concentration des %s par panier (HHI, 0–10 000)",
    gauge = list(extraEu = "Hors UE", hub = "Via BE/NL", top = "Premier",
                 total = "Valeur"),
    levels = list(diversified = "Diversifié", moderate = "Modéré",
                  concentrated = "Concentré", none = "Pas de données"),
    mapNote = "Le partenaire est le pays déclaré dans les statistiques (expédition ou destination), pas le pays d'origine ou de destination finale ; BE et NL sont des hubs de transit.",
    mapLegend = "Part du flux", luxLegend = "Luxembourg", hubLegend = "Hub exclu",
    wholeBasket = "Ensemble du panier",
    prodCols = c("Produit", "Valeur (M€)", "HHI", "Niveau", "Hors UE"),
    partnerCols = c("Partenaire", "Part", "Valeur (M€)", "Bloc"),
    partnerTitle = "Principaux partenaires", hubFlag = " (hub)",
    hubsExcludedSuffix = " · BE/NL exclus", unspecified = "Non spécifié",
    blocEu = "UE", blocExtra = "Hors UE",
    trendTitle = "%s : concentration des %s depuis %d",
    trendConcentrated = "Concentré", trendModerate = "Modéré",
    balanceTitle = "Importations et exportations · %s",
    stressTitle = "Test de stress", stressEvent = "Événement",
    stressNote = "Variation annuelle de la valeur totale. L'« après » est l'année %d : données annuelles, donc l'année de l'événement mélange des mois avant et après.",
    stressNone = "Aucun événement ne tombe dans la plage de données (il faut au moins une année avant l'événement).",
    event = "Événement :",
    kpi = list(change = "Valeur %d vs. %d", hhi = "HHI %d → %d",
               weakest = "Plus forte baisse depuis %d"),
    shiftTitle = "Adapter · évolution des parts de %s, %d vs. %d",
    shiftCols = c("Partenaire", "Avant", "Après", "Δ pp"),
    careTitle = "À lire avec prudence",
    footer = "Source : Eurostat Comext DS-045409, déclarant Luxembourg, valeurs annuelles en euros, chapitres HS2. HHI calculé sur les pays partenaires uniquement ; les partenaires « non spécifiés » comptent dans les totaux mais pas dans les parts. HHI d'un panier = moyenne des HHI des chapitres pondérée par la valeur. L'appartenance à l'UE est évaluée année par année. Paniers : Stratégie nationale de résilience (HCPN, 2025), transposés en chapitres HS2.",
    tabs = list(resist = "Résister", adapt = "Adapter",
                method = "Méthode et limites"),
    sidebarBasket = "Panier",
    resistIntro = "Quelle est la dépendance du Luxembourg vis-à-vis de ses partenaires ? Cliquez sur un panier pour changer la sélection.",
    adaptIntro = "Comment les partenaires ont-ils évolué autour d'un choc ? La sélection (flux, panier, produit) est celle de l'onglet « Résister ».",
    adaptContext = "Sélection : %s · %s",
    errors = list(year = "Année inconnue.", noData = "Pas de données pour cette sélection.",
                  event = "Événement hors de la plage de données.")
  ),
  care = list(
    list(title = "Partenaire ≠ origine",
         text = "Les statistiques enregistrent le pays d'expédition ou de destination. Un produit transitant par un hub est attribué au hub."),
    list(title = "Concentration ≠ risque",
         text = "Un HHI élevé signale une dépendance, pas une menace : tout dépend de la fiabilité et de la substituabilité du partenaire."),
    list(title = "Chapitres HS2",
         text = "Un chapitre regroupe des produits très différents : le HHI d'un chapitre masque la concentration au niveau des produits fins."),
    list(title = "Valeurs en euros courants",
         text = "Pas de volumes dans les données : les variations de valeur mélangent prix et quantités, et l'inflation n'est pas corrigée.")
  )
)
lbl <- cfg$labels

# 2. DONNÉES (chargées une seule fois) ----------------------------------------

if (!file.exists(cfg$dataPath)) {
  stop("Fichier de données absent : ", cfg$dataPath,
       " (lancer prepareData.R).", call. = FALSE)
}
dataStore <- readRDS(cfg$dataPath)
trade     <- dataStore$trade
setkey(trade, flow, year)
years     <- dataStore$years
firstYear <- min(years)
lastYear  <- max(years)
unspecifiedCodes <- dataStore$unspecified

flows <- cfg$flows[purrr::map_lgl(cfg$flows, function(f) f$code %in% trade$flow)]
if (length(flows) == 0L) stop("Aucun flux du dictionnaire dans les données.", call. = FALSE)
defaultFlow <- if (cfg$defaults$flow %in% names(flows)) cfg$defaults$flow else names(flows)[1]

euMembersAt <- function(year) {
  until <- cfg$euUntil[names(cfg$euFrom)]
  until[is.na(until)] <- Inf
  names(cfg$euFrom)[cfg$euFrom <= year & until >= year]
}
euByYear <- setNames(purrr::map(years, euMembersAt), as.character(years))

buildBaskets <- function(baskets, chapters, labelDict) {
  chapters <- sort(setdiff(chapters, cfg$allExclude))
  baskets[[cfg$allBasket]]$products <- setNames(
    ifelse(is.na(labelDict[chapters]), chapters, labelDict[chapters]), chapters)
  filtered <- purrr::map(baskets, function(b) {
    b$products <- b$products[names(b$products) %in% chapters]
    b
  })
  filtered[purrr::map_int(filtered, function(b) length(b$products)) > 0L]
}
baskets <- buildBaskets(cfg$baskets, unique(trade$product), dataStore$products)
missingCodes <- setdiff(unlist(purrr::map(cfg$baskets[names(cfg$baskets) != cfg$allBasket],
                                          function(b) names(b$products))),
                        unique(trade$product))
if (length(missingCodes) > 0L) {
  message("Chapitres des paniers absents des données : ", paste(missingCodes, collapse = ", "))
}
defaultBasket <- if (cfg$defaults$basket %in% names(baskets)) cfg$defaults$basket else
  names(baskets)[1]

productLabels <- unlist(unname(purrr::map(
  baskets[names(baskets) != cfg$allBasket], function(b) b$products)))
productLabels <- c(productLabels,
                   baskets[[cfg$allBasket]]$products[!names(baskets[[cfg$allBasket]]$products) %in%
                                                       names(productLabels)])
partnerNames <- sub(",.*$", "", sub("\\s*\\(.*$", "", dataStore$partners))

validEvents <- cfg$events[purrr::map_lgl(cfg$events, function(ev) {
  ev$year > firstYear && ev$year <= lastYear
})]

# 3. FONCTIONS UTILITAIRES ----------------------------------------------------

fmtNumber <- function(x, digits = 0) {
  format(round(x, digits), big.mark = "\u202f", decimal.mark = ",",
         nsmall = digits, scientific = FALSE, trim = TRUE)
}
fmtPct <- function(x, digits = 0) {
  ifelse(is.finite(x), paste0(fmtNumber(x * 100, digits), " %"), "–")
}
fmtSigned <- function(x, digits = 0) {
  paste0(ifelse(is.finite(x) & x >= 0, "+", ""), fmtPct(x, digits))
}
fmtHhi <- function(x) ifelse(is.finite(x), fmtNumber(x, 0), "–")

fmtEur <- function(x) {
  if (!is.finite(x)) return("–")
  a <- abs(x)
  if (a >= 1e9) return(paste0(fmtNumber(x / 1e9, 2), " Md€"))
  if (a >= 1e6) return(paste0(fmtNumber(x / 1e6, if (a >= 1e8) 0 else 1), " M€"))
  if (a >= 1e3) return(paste0(fmtNumber(x / 1e3, 0), " k€"))
  paste0(fmtNumber(x, 0), " €")
}

getLevel <- function(hhi) {
  key <- if (!is.finite(hhi)) "none"
  else if (hhi > cfg$thresholds[["concentrated"]]) "concentrated"
  else if (hhi > cfg$thresholds[["moderate"]]) "moderate"
  else "diversified"
  list(key = key, label = lbl$levels[[key]], colour = cfg$colours$levels[[key]])
}

computeMetrics <- function(trade, codes, flowCode, yr, hubsExcluded) {
  emptyShares <- data.table(partner = character(), value = numeric(), share = numeric())
  empty <- list(total = 0, hhi = NA_real_, ext = NA_real_, hub = NA_real_,
                shares = emptyShares)
  agg <- trade[.(flowCode, yr), nomatch = NULL][product %chin% codes]
  agg <- agg[, .(value = sum(value)), by = .(product, partner)][value != 0]
  if (nrow(agg) == 0L) return(empty)
  euSet <- euByYear[[as.character(yr)]]
  agg[, `:=`(isUnspec = partner %chin% unspecifiedCodes,
             isHub    = partner %chin% cfg$hubs,
             isEu     = partner %chin% euSet)]
  agg[, inShares := !isUnspec & !(hubsExcluded & isHub)]
  byProduct <- agg[, {
    ctP <- sum(value[inShares])
    .(total = sum(value),
      ctAll = sum(value[!isUnspec]),
      ct    = ctP,
      ext   = sum(value[inShares & !isEu]),
      hub   = sum(value[isHub & !isUnspec]),
      hhi   = if (ctP > 0) sum((100 * value[inShares] / ctP)^2) else NA_real_)
  }, by = product]
  valid <- byProduct[ct > 0 & is.finite(hhi) & total > 0]
  hhi <- if (nrow(valid) > 0L) weighted.mean(valid$hhi, valid$total) else NA_real_
  shares <- agg[inShares == TRUE, .(value = sum(value)), by = partner]
  if (nrow(shares) > 0L) {
    shares[, share := value / sum(value)]
    setorder(shares, -share)
  } else shares <- emptyShares
  ct <- sum(byProduct$ct); ctAll <- sum(byProduct$ctAll)
  list(total = sum(byProduct$total), hhi = hhi,
       ext = if (ct > 0) sum(byProduct$ext) / ct else NA_real_,
       hub = if (ctAll > 0) sum(byProduct$hub) / ctAll else NA_real_,
       shares = shares)
}

seriesTotals <- function(trade, codes, flowCode) {
  agg <- trade[.(flowCode), nomatch = NULL][product %chin% codes,
                                            .(value = sum(value)), by = year]
  out <- setNames(numeric(length(years)), years)
  out[as.character(agg$year)] <- agg$value
  out
}

classifyShare <- function(share, steps) {
  cls <- pmin(length(steps), pmax(1L, findInterval(share, steps)))
  cls[is.na(share) | share <= 0] <- 0L
  as.integer(cls)
}

shareClassLabels <- function(steps) {
  n <- length(steps)
  pct <- function(x) fmtPct(x, digits = if (x < 0.01) 1 else 0)
  vapply(seq_len(n), function(k) {
    if (k == 1L) paste0("< ", pct(steps[2]))
    else if (k == n) paste0("≥ ", pct(steps[n]))
    else paste0(pct(steps[k]), "–", pct(steps[k + 1L]))
  }, character(1))
}

loadWorld <- function() {
  if (!requireNamespace("rnaturalearth", quietly = TRUE)) {
    stop("Package 'rnaturalearth' (et 'rnaturalearthdata') requis.", call. = FALSE)
  }
  w <- rnaturalearth::ne_countries(scale = "medium", returnclass = "sf")
  isoCol <- intersect(c("iso_a2_eh", "iso_a2"), names(w))[1]
  w$iso <- w[[isoCol]]
  w$iso[w$iso %in% "-99"] <- NA_character_
  if ("continent" %in% names(w)) w <- w[w$continent != "Antarctica", ]
  w[, "iso"]
}
world <- loadWorld()

partnerLabel <- function(codes) {
  base <- unname(partnerNames[codes])
  base <- ifelse(codes %in% unspecifiedCodes, lbl$unspecified, base)
  base <- ifelse(is.na(base), codes, base)
  paste0(base, ifelse(codes %in% cfg$hubs, lbl$hubFlag, ""))
}

# 4. FONCTIONS GRAPHIQUES -----------------------------------------------------
# CONTENU STRICTEMENT IDENTIQUE à la version précédente.

baseTheme <- function() {
  theme_minimal(base_size = 12) +
    theme(panel.grid.minor = element_blank(),
          plot.margin = margin(8, 12, 8, 8))
}

plotMap <- function(world, shares, view, hubsExcluded) {
  vw <- cfg$mapViews[[view]]
  steps <- cfg$shareSteps
  world$share <- shares$share[match(world$iso, shares$partner)]
  world$cls <- classifyShare(world$share, steps)
  world$fillKey <- ifelse(world$iso %in% cfg$lux, "lux",
                          ifelse(hubsExcluded & world$iso %in% cfg$hubs, "hub",
                                 as.character(world$cls)))
  ramp <- colorRampPalette(cfg$colours$seqRamp)(length(steps))
  fills <- c(setNames(cfg$colours$noImport, "0"),
             setNames(ramp, as.character(seq_along(steps))),
             hub = cfg$colours$hub, lux = cfg$colours$lux)
  labs <- c(setNames("–", "0"),
            setNames(shareClassLabels(steps), as.character(seq_along(steps))),
            hub = lbl$hubLegend, lux = lbl$luxLegend)
  usedKeys <- c(as.character(seq_along(steps)), "lux", if (hubsExcluded) "hub")
  luxDf <- data.frame(lon = cfg$luxPoint[["lon"]], lat = cfg$luxPoint[["lat"]])
  ggplot(world) +
    geom_sf(aes(fill = fillKey), colour = "white", linewidth = 0.15) +
    geom_point(data = luxDf, aes(lon, lat), shape = 21, size = 3.5,
               stroke = 1.2, fill = NA, colour = "black") +
    scale_fill_manual(values = fills, breaks = usedKeys, labels = labs[usedKeys],
                      name = lbl$mapLegend, drop = FALSE) +
    coord_sf(xlim = vw$xlim, ylim = vw$ylim, expand = FALSE, crs = vw$crs,
             default_crs = sf::st_crs(4326)) +
    theme_void() +
    theme(legend.position = "bottom")
}

plotTrend <- function(series, events) {
  series <- series[is.finite(hhi)]
  validate(need(nrow(series) > 0L, lbl$errors$noData))
  thr <- cfg$thresholds
  yMax <- max(cfg$trend$minYMax,
              ceiling(max(series$hhi) / cfg$trend$yStep) * cfg$trend$yStep)
  xRange <- range(series$year)
  evDt <- rbindlist(c(list(data.table(year = integer(), label = character())),
                      unname(purrr::map(events, function(ev) {
                        data.table(year = ev$year, label = ev$label)
                      }))))
  evDt <- evDt[year >= xRange[1] & year <= xRange[2]]
  last <- series[.N]
  accent <- cfg$colours$accent
  ggplot(series, aes(year, hhi)) +
    annotate("rect", xmin = -Inf, xmax = Inf, ymin = thr[["concentrated"]],
             ymax = yMax, fill = cfg$colours$levels[["concentrated"]], alpha = 0.08) +
    annotate("rect", xmin = -Inf, xmax = Inf, ymin = thr[["moderate"]],
             ymax = thr[["concentrated"]],
             fill = cfg$colours$levels[["moderate"]], alpha = 0.08) +
    geom_hline(yintercept = unname(thr), linetype = "dashed",
               colour = cfg$colours$grey) +
    annotate("text", x = xRange[2], y = thr[["concentrated"]], vjust = -0.5,
             hjust = 1, size = 3, label = lbl$trendConcentrated) +
    annotate("text", x = xRange[2], y = thr[["moderate"]], vjust = -0.5,
             hjust = 1, size = 3, label = lbl$trendModerate) +
    geom_area(fill = accent, alpha = 0.12) +
    geom_line(colour = accent, linewidth = 1) +
    geom_point(colour = accent, size = 1.8) +
    geom_vline(data = evDt, aes(xintercept = year), colour = cfg$colours$grey) +
    geom_text(data = evDt, aes(x = year, y = yMax, label = label), hjust = -0.05,
              vjust = 1.5, size = 3, angle = 0, inherit.aes = FALSE) +
    geom_text(data = last, aes(label = fmtHhi(hhi)), hjust = -0.3, size = 3.5) +
    scale_x_continuous(breaks = scales::breaks_pretty(n = 10),
                       expand = expansion(mult = c(0.01, 0.08))) +
    scale_y_continuous(limits = c(0, yMax), labels = fmtHhi) +
    labs(x = NULL, y = "HHI") +
    baseTheme()
}

plotBalance <- function(dt) {
  validate(need(nrow(dt) > 0L, lbl$errors$noData))
  flowLabels <- purrr::map_chr(flows, function(f) f$label)
  ggplot(dt, aes(year, value, colour = flowKey)) +
    geom_line(linewidth = 1) + geom_point(size = 1.8) +
    scale_colour_manual(values = cfg$colours$flows, labels = flowLabels, name = NULL) +
    scale_x_continuous(breaks = scales::breaks_pretty(n = 10)) +
    scale_y_continuous(labels = function(x) fmtNumber(x, 0)) +
    labs(x = NULL, y = "M€") +
    baseTheme() +
    theme(legend.position = "bottom")
}

plotStress <- function(yoy, y0) {
  d <- copy(yoy)[is.finite(change)]
  validate(need(nrow(d) > 0L, lbl$errors$noData))
  d[, `:=`(dir = fifelse(change >= 0, "pos", "neg"),
           phase = fifelse(year < y0, "pre", "post"))]
  ggplot(d, aes(year, change, fill = dir, alpha = phase)) +
    geom_col(width = 0.7) +
    geom_hline(yintercept = 0, colour = cfg$colours$grey) +
    geom_vline(xintercept = y0 - 0.5, linetype = "dashed") +
    annotate("text", x = y0 - 0.4, y = Inf, hjust = 0, vjust = 1.5, size = 3.2,
             label = paste(lbl$event, y0)) +
    scale_fill_manual(values = c(pos = cfg$colours$positive,
                                 neg = cfg$colours$negative), guide = "none") +
    scale_alpha_manual(values = c(pre = 0.45, post = 1), guide = "none") +
    scale_x_continuous(breaks = d$year) +
    scale_y_continuous(labels = function(x) paste0(ifelse(x > 0, "+", ""),
                                                   round(x * 100), " %")) +
    labs(x = NULL, y = NULL) +
    baseTheme()
}

# 5. STYLES -------------------------------------------------------------------
# Barre de filtres nettement compactée : padding, gap et contrôles réduits.

INK       <- "#191622"
INK_2     <- "#4A4458"
INK_3     <- "#8B8394"
PAPER     <- "#F4F0E8"
PAPER_2   <- "#EDE7DB"
CARD      <- "#FFFFFF"
RULE      <- "#E0D8C8"
RULE_2    <- "#CFC5B2"
PRIMARY   <- "#5B1E5C"
ACCENT    <- "#C9512B"

buildCss <- function() {
  paste0('
:root{
  --ink:', INK, '; --ink-2:', INK_2, '; --ink-3:', INK_3, ';
  --paper:', PAPER, '; --paper-2:', PAPER_2, '; --card:', CARD, ';
  --rule:', RULE, '; --rule-2:', RULE_2, ';
  --primary:', PRIMARY, '; --accent:', ACCENT, ';
}
html,body{
  background:var(--paper);
  color:var(--ink);
  font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  -webkit-font-smoothing:antialiased;
  font-feature-settings:"ss01","cv11","tnum";
}
h1,h2,h3,h4,h5,h6{
  font-family:"Manrope","Inter",-apple-system,sans-serif;
  font-weight:600;
  letter-spacing:-.015em;
  color:var(--ink);
}

/* ============ HEADER ============ */
.app-header{
  padding:2.5rem 2.5rem 1.75rem;
  border-bottom:1px solid var(--rule);
}
.header-top{
  display:flex;justify-content:space-between;align-items:flex-end;
  gap:2rem;flex-wrap:wrap;margin-bottom:1.5rem;
}
.header-eyebrow{
  font-size:.68rem;text-transform:uppercase;letter-spacing:.2em;
  font-weight:600;color:var(--accent);
  padding-bottom:.35rem;border-bottom:1px solid var(--accent);
  display:inline-block;
}
.header-meta{display:flex;gap:2rem;flex-wrap:wrap}
.header-meta .item{display:flex;flex-direction:column;gap:.15rem}
.header-meta em{
  font-style:normal;font-size:.62rem;text-transform:uppercase;
  letter-spacing:.14em;color:var(--ink-3);font-weight:600;
}
.header-meta strong{
  font-family:"JetBrains Mono",ui-monospace,monospace;
  font-size:.92rem;font-weight:500;color:var(--ink);
}
.app-header h1{
  font-size:clamp(2.1rem,4.2vw,3rem);
  line-height:1;margin:0 0 .75rem;font-weight:600;
  letter-spacing:-.03em;
}
.app-header h1 em{font-style:normal;color:var(--primary);font-weight:600}
.app-header .tagline{
  font-size:.98rem;color:var(--ink-2);max-width:66ch;
  line-height:1.55;margin:0;
}

/* ============ FILTRE COMPACT ============ */
.filter-bar{
  position:sticky;top:0;z-index:200;
  background:var(--paper);
  border-bottom:1px solid var(--rule);
  padding:.45rem 2.5rem;
  display:flex;flex-wrap:wrap;align-items:center;
  gap:.3rem 1rem;
  font-size:.78rem;
  line-height:1.2;
  min-height:0;
}
.filter-group{display:flex;align-items:center;gap:.4rem;margin:0}
.filter-label{
  font-size:.58rem;text-transform:uppercase;letter-spacing:.12em;
  font-weight:700;color:var(--ink-3);
  line-height:1;margin:0;padding:0;
  white-space:nowrap;
}
.filter-bar .form-group{margin-bottom:0 !important}
.filter-bar .form-control,
.filter-bar .form-select{
  border:1px solid var(--rule-2);border-radius:2px;
  background:#fff;font-size:.76rem;color:var(--ink);
  padding:.16rem .45rem;height:auto;
  line-height:1.25;min-height:22px;
  font-family:inherit;
  box-shadow:none;
}
.filter-bar .form-control:focus,
.filter-bar .form-select:focus{
  border-color:var(--primary);
  box-shadow:0 0 0 2px rgba(91,30,92,.1);
}
.filter-bar .form-check-inline{margin:0 !important;padding:0 !important}
.filter-bar .form-check-inline input[type="radio"]{display:none}
.filter-bar .form-check-inline label,
.filter-bar .form-check-inline .form-check-label{
  display:inline-flex;align-items:center;
  padding:.16rem .55rem;
  border:1px solid var(--rule-2);border-radius:2px;
  font-size:.74rem;color:var(--ink-2);font-weight:500;
  cursor:pointer;background:#fff;
  transition:all .15s ease;margin:0;margin-right:-1px;
  line-height:1.3;
}
.filter-bar .form-check-inline label:hover{background:var(--paper-2);color:var(--ink)}
.filter-bar .form-check-inline input:checked + label{
  background:var(--ink);color:#fff;border-color:var(--ink);
}
.filter-bar .checkbox label,
.filter-bar .form-check:not(.form-check-inline) label{
  font-size:.74rem;color:var(--ink-2);font-weight:500;
  margin:0;line-height:1.3;
}
.filter-bar .form-check-input{
  width:13px;height:13px;margin:0 .35rem 0 0;
  vertical-align:middle;
}
.filter-bar .form-check-input:checked{
  background-color:var(--primary);border-color:var(--primary);
}

/* ============ NAVIGATION : petites puces ============ */
.nav-pills{
  padding:.8rem 2.5rem !important;
  gap:.4rem !important;
  border-bottom:1px solid var(--rule) !important;
  background:var(--paper) !important;
  display:flex !important;
  flex-wrap:wrap !important;
  align-items:center;
}
.nav-pills .nav-item{margin:0 !important}
.nav-pills .nav-link{
  padding:.42rem 1rem !important;
  border:1px solid var(--rule-2) !important;
  border-radius:999px !important;
  font-family:"Manrope","Inter",sans-serif !important;
  font-size:.82rem !important;
  font-weight:600 !important;
  color:var(--ink-2) !important;
  background:#fff !important;
  transition:all .15s ease !important;
  display:inline-flex !important;
  align-items:center !important;
  gap:.45rem !important;
  line-height:1 !important;
}
.nav-pills .nav-link:hover{
  background:var(--paper-2) !important;
  border-color:var(--ink-3) !important;
  color:var(--ink) !important;
}
.nav-pills .nav-link.active{
  background:var(--ink) !important;
  color:#fff !important;
  border-color:var(--ink) !important;
  box-shadow:0 4px 12px -6px rgba(25,22,34,.35);
}
.nav-pills .nav-link .tab-num{
  font-family:"JetBrains Mono",ui-monospace,monospace;
  font-size:.68rem;font-weight:700;
  letter-spacing:.05em;color:var(--accent);
}
.nav-pills .nav-link.active .tab-num{color:#F0A85B}

/* ============ MAIN CONTENT ============ */
.tab-content,
.tab-pane{
  padding:1.75rem 2.5rem 3rem;
  background:var(--paper);
}
.intro{
  font-size:.9rem;color:var(--ink-2);
  line-height:1.6;max-width:78ch;
  margin:0 0 1.4rem;
  padding-left:1rem;
  border-left:2px solid var(--accent);
}
.section-title{
  display:flex;align-items:baseline;gap:.9rem;
  font-family:"Manrope","Inter",sans-serif;
  font-size:1.08rem;font-weight:600;
  color:var(--ink);
  margin:0 0 1rem;
  padding-bottom:.65rem;
  border-bottom:1px solid var(--rule);
  letter-spacing:-.01em;
}
.section-title .num{
  font-family:"JetBrains Mono",monospace;
  font-size:.7rem;color:var(--accent);font-weight:700;
  letter-spacing:.1em;
}

/* ============ CARDS ============ */
.card{
  background:var(--card);
  border:1px solid var(--rule);
  border-radius:2px;
  box-shadow:none;
  transition:border-color .2s ease;
  overflow:hidden;
}
.card:hover{border-color:var(--rule-2)}
.card-header{
  background:transparent;
  border-bottom:1px solid var(--rule);
  padding:.8rem 1.15rem;
  font-family:"Manrope","Inter",sans-serif;
  font-weight:600;
  font-size:.9rem;
  letter-spacing:-.01em;
  color:var(--ink);
  text-transform:none;
  line-height:1.35;
}
.card-body{padding:1.1rem 1.25rem 1.3rem}

/* ============ GAUGES ============ */
.gaugeStrip{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(215px,1fr));
  gap:14px;
  margin-bottom:24px;
}
.gauge{
  display:flex;flex-direction:column;gap:.6rem;
  text-align:left;
  padding:1.1rem 1.1rem .95rem;
  background:#fff;
  border:1px solid var(--rule);
  border-top:3px solid var(--ink);
  border-radius:2px;
  cursor:pointer;
  transition:all .2s ease;
  font-family:inherit;
  color:inherit;
  outline:none;
  position:relative;
}
.gauge:hover{
  border-color:var(--rule-2);
  border-top-color:var(--primary);
  transform:translateY(-2px);
}
.gauge:focus-visible{box-shadow:0 0 0 3px rgba(91,30,92,.18)}
.gauge.active{
  border-top-color:var(--accent);
  box-shadow:0 0 0 1px var(--accent) inset;
  background:linear-gradient(180deg, rgba(201,81,43,.03) 0%, #fff 45%);
}
.gTop{
  display:flex;justify-content:space-between;align-items:center;
  margin-bottom:.1rem;
}
.gNum{
  font-family:"JetBrains Mono",monospace;
  font-size:.68rem;color:var(--ink-3);
  letter-spacing:.1em;font-weight:600;
}
.gPill{
  color:#fff;font-size:.6rem;
  font-weight:700;text-transform:uppercase;
  letter-spacing:.1em;
  padding:2px 8px;border-radius:2px;
}
.gName{
  font-family:"Manrope","Inter",sans-serif;
  font-size:1rem;font-weight:600;
  color:var(--ink);letter-spacing:-.01em;
  line-height:1.25;
}
.gBig{
  display:flex;align-items:baseline;gap:.4rem;
  margin:.35rem 0 .3rem;
  font-family:"Manrope","Inter",sans-serif;
  font-size:2.3rem;font-weight:600;
  letter-spacing:-.035em;line-height:1;
  color:var(--ink);
  font-variant-numeric:tabular-nums;
}
.gBig small{
  font-family:"JetBrains Mono",monospace;
  font-size:.62rem;font-weight:600;
  color:var(--ink-3);letter-spacing:.14em;
}
.gBar{
  display:block;height:2px;
  background:var(--rule);
  overflow:hidden;
  margin:.15rem 0 .5rem;
}
.gBar i{display:block;height:100%;transition:width .5s ease}
.gStats{
  display:grid;grid-template-columns:1fr 1fr;
  gap:.4rem .8rem;
  margin:0;padding:.75rem 0 0;
  border-top:1px solid var(--rule);
}
.gStats dt{
  font-size:.68rem;color:var(--ink-3);
  font-weight:500;letter-spacing:.02em;
  grid-column:1;margin:0;
}
.gStats dd{
  font-family:"JetBrains Mono",monospace;
  font-size:.82rem;color:var(--ink);
  font-weight:500;margin:0;
  grid-column:2;text-align:right;
  font-variant-numeric:tabular-nums;
}

/* ============ KPI ============ */
.kpiRow{
  display:grid;grid-template-columns:repeat(3,1fr);
  gap:1rem;margin:1.4rem 0 1rem;
}
@media(max-width:900px){.kpiRow{grid-template-columns:1fr}}
.kpi{
  background:#fff;border:1px solid var(--rule);
  border-left:3px solid var(--accent);
  border-radius:2px;
  padding:1rem 1.15rem;
}
.kpi .l{
  display:block;font-size:.66rem;
  color:var(--ink-3);text-transform:uppercase;
  letter-spacing:.14em;font-weight:700;
  margin-bottom:.5rem;
}
.kpi .v{
  display:block;
  font-family:"Manrope","Inter",sans-serif;
  font-size:1.7rem;font-weight:600;
  letter-spacing:-.02em;
  color:var(--ink);
  font-variant-numeric:tabular-nums;
  line-height:1;
}

/* ============ CONTEXT BANNER ============ */
.context-banner{
  display:flex;align-items:center;gap:.9rem;
  padding:.95rem 1.2rem;
  background:#fff;
  border:1px solid var(--rule);
  border-left:3px solid var(--primary);
  border-radius:2px;
  font-size:.9rem;color:var(--ink-2);
  margin:1rem 0 1.5rem;
}
.context-banner strong{
  font-family:"Manrope","Inter",sans-serif;
  color:var(--ink);font-weight:600;
  font-size:1rem;
}

/* ============ NOTES ============ */
.note{font-size:.82rem;color:var(--ink-3);line-height:1.6}
.note-mono{
  font-family:"JetBrains Mono",monospace;
  font-size:.76rem;color:var(--ink-3);
  letter-spacing:.02em;
}

/* ============ CARE CARDS ============ */
.care-grid{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  gap:1rem;padding:.25rem 0 .5rem;
}
.care-card{
  padding:1.25rem 1.25rem 1.35rem;
  background:#fff;
  border:1px solid var(--rule);
  border-top:3px solid var(--primary);
  border-radius:2px;
  height:100%;
}
.care-card .num{
  font-family:"JetBrains Mono",monospace;
  font-size:.68rem;color:var(--accent);
  letter-spacing:.14em;font-weight:600;
  display:block;margin-bottom:.75rem;
}
.care-card h6{
  font-family:"Manrope","Inter",sans-serif;
  font-size:1rem;font-weight:600;
  margin:0 0 .6rem;color:var(--ink);
  letter-spacing:-.01em;
}
.care-card p{
  font-size:.83rem;color:var(--ink-2);
  line-height:1.62;margin:0;
}

/* ============ FOOTER ============ */
.app-footer{
  margin-top:2rem;
  padding:1.35rem 1.5rem;
  background:#fff;
  border:1px solid var(--rule);
  border-left:3px solid var(--ink);
  border-radius:2px;
  font-size:.78rem;color:var(--ink-3);
  line-height:1.7;
}

/* ============ TABLES ============ */
.dataTables_wrapper{font-size:.85rem}
table.dataTable{border-collapse:collapse !important}
table.dataTable thead th{
  background:transparent !important;
  border:none !important;
  border-bottom:1px solid var(--ink) !important;
  font-family:"Inter",sans-serif !important;
  font-weight:700 !important;
  color:var(--ink) !important;
  text-transform:uppercase;
  font-size:.66rem !important;
  letter-spacing:.14em;
  padding:9px 11px !important;
  white-space:nowrap;
}
table.dataTable tbody td{
  padding:11px 11px !important;
  border:none !important;
  border-bottom:1px solid var(--rule) !important;
  color:var(--ink);
  font-variant-numeric:tabular-nums;
  font-family:"Inter",sans-serif;
}
table.dataTable tbody tr{transition:background .12s ease}
table.dataTable tbody tr:hover td{background:var(--paper-2) !important}
table.dataTable tbody tr.selected td{
  background:rgba(201,81,43,.08) !important;
  color:var(--ink) !important;
}
table.dataTable tbody tr.selected td:first-child{
  box-shadow:inset 3px 0 0 var(--accent);
}

/* ============ SCROLLBAR ============ */
::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--rule-2);border-radius:0}
::-webkit-scrollbar-thumb:hover{background:var(--ink-3)}

.dataTables_scrollBody{border:none !important}

/* ============ GRAPHS FULL WIDTH ============ */
.chart-wide .card-body{padding:1.25rem 1.5rem 1.5rem}
.chart-wide .shiny-plot-output{width:100% !important}
')
}

# 6. COMPOSANTS UI ------------------------------------------------------------

makeGauge <- function(id, label, m, active, idx) {
  lv <- getLevel(m$hhi)
  top <- if (nrow(m$shares) > 0L) {
    paste(partnerLabel(m$shares$partner[1]), fmtPct(m$shares$share[1]))
  } else "–"
  widthPct <- if (is.finite(m$hhi)) min(100, 100 * m$hhi / cfg$hhiMax) else 0
  tags$button(
    type = "button",
    class = paste("gauge", if (active) "active"),
    onclick = sprintf("Shiny.setInputValue('basketClick', '%s', {priority: 'event'})", id),
    tags$div(class = "gTop",
             tags$span(class = "gNum", sprintf("%02d", idx)),
             tags$span(class = "gPill", style = sprintf("background:%s", lv$colour), lv$label)
    ),
    tags$div(class = "gName", label),
    tags$div(class = "gBig",
             tags$span(fmtHhi(m$hhi)),
             tags$small("HHI")
    ),
    tags$div(class = "gBar",
             tags$i(style = sprintf("width:%.1f%%;background:%s", widthPct, lv$colour))),
    tags$dl(class = "gStats",
            tags$dt(lbl$gauge$extraEu), tags$dd(fmtPct(m$ext)),
            tags$dt(lbl$gauge$hub),     tags$dd(fmtPct(m$hub)),
            tags$dt(lbl$gauge$top),     tags$dd(top),
            tags$dt(lbl$gauge$total),   tags$dd(fmtEur(m$total))
    )
  )
}

kpiCard <- function(label, value) {
  div(class = "kpi", tags$span(class = "l", label), tags$span(class = "v", value))
}

stressCard <- function() {
  if (length(validEvents) == 0L) {
    return(div(class = "card",
               div(class = "card-header", lbl$stressTitle),
               div(class = "card-body",
                   p(class = "note", lbl$stressNone))))
  }
  div(class = "card",
      div(class = "card-header", lbl$stressTitle),
      div(class = "card-body",
          radioButtons("event", lbl$stressEvent, inline = TRUE,
                       choices = setNames(names(validEvents),
                                          purrr::map_chr(validEvents, function(e) e$label)),
                       selected = names(validEvents)[1]),
          div(class = "note", textOutput("evNote")),
          uiOutput("stKpis"),
          plotOutput("stChart", height = "280px"),
          h6(class = "mt-3", textOutput("shiftTitle", inline = TRUE)),
          DT::DTOutput("shiftTable")
      )
  )
}

# 7. INTERFACE ----------------------------------------------------------------

basketChoices <- setNames(names(baskets),
                          purrr::map_chr(baskets, function(b) b$label))

tab_label <- function(num, text) {
  tagList(
    tags$span(class = "tab-num", num),
    tags$span(text)
  )
}

ui <- bslib::page_fluid(
  theme = bslib::bs_theme(
    version = 5,
    primary = PRIMARY,
    bg = PAPER,
    fg = INK,
    base_font    = bslib::font_google("Inter"),
    heading_font = bslib::font_google("Manrope"),
    code_font    = bslib::font_google("JetBrains Mono"),
    "border-radius"    = "2px",
    "border-radius-lg" = "2px",
    "border-radius-sm" = "2px"
  ),
  tags$head(tags$style(HTML(buildCss()))),
  
  # ---------- Header éditorial ----------
  tags$header(class = "app-header",
              div(class = "header-top",
                  tags$span(class = "header-eyebrow", lbl$eyebrow),
                  div(class = "header-meta",
                      div(class = "item", tags$em(lbl$lastYear), tags$strong(lastYear)),
                      div(class = "item", tags$em(lbl$release),  tags$strong(dataStore$updated))
                  )
              ),
              h1("Radar de ", tags$em("résilience")),
              p(class = "tagline", lbl$subtitle)
  ),
  
  # ---------- Barre de filtres compacte ----------
  div(class = "filter-bar",
      div(class = "filter-group",
          tags$span(class = "filter-label", lbl$flow),
          radioButtons("flow", NULL, inline = TRUE,
                       choices = setNames(names(flows),
                                          purrr::map_chr(flows, function(f) f$label)),
                       selected = defaultFlow)
      ),
      div(class = "filter-group",
          tags$span(class = "filter-label", lbl$sidebarBasket),
          selectInput("basket", NULL, choices = basketChoices,
                      selected = defaultBasket, width = "160px")
      ),
      div(class = "filter-group",
          checkboxInput("hubs", lbl$hubsToggle, value = FALSE)
      ),
      conditionalPanel(
        condition = "input.tabs == 'resist'",
        div(class = "filter-group",
            tags$span(class = "filter-label", lbl$year),
            selectInput("year", NULL, choices = rev(years),
                        selected = lastYear, width = "100px")
        ),
        div(class = "filter-group",
            tags$span(class = "filter-label", lbl$mapView),
            radioButtons("mapView", NULL, inline = TRUE,
                         choices = setNames(names(cfg$mapViews),
                                            purrr::map_chr(cfg$mapViews, function(v) v$label)),
                         selected = cfg$defaults$mapView)
        )
      )
  ),
  
  # ---------- Onglets : petites puces ----------
  bslib::navset_pill(
    id = "tabs",
    
    bslib::nav_panel(
      title = tab_label("01", lbl$tabs$resist), value = "resist",
      p(class = "intro", lbl$resistIntro),
      div(class = "section-title",
          span(class = "num", "01"),
          span(textOutput("gaugeTitle", inline = TRUE))),
      uiOutput("gauges"),
      fluidRow(
        column(6, div(class = "card mb-3",
                      div(class = "card-header", textOutput("mapTitle", inline = TRUE)),
                      div(class = "card-body",
                          div(class = "note-mono", textOutput("mapCrumb")),
                          plotOutput("map", height = "420px"),
                          div(class = "note", lbl$mapNote)))),
        column(6, div(class = "card mb-3",
                      div(class = "card-header", textOutput("drillTitle", inline = TRUE)),
                      div(class = "card-body",
                          DT::DTOutput("prodTable"),
                          hr(),
                          div(class = "section-title", span(class = "num", "02"),
                              span(textOutput("partnerFor", inline = TRUE))),
                          DT::DTOutput("partnerTable"))))
      ),
      # --- Graphiques empilés en PLEINE LARGEUR ---
      div(class = "card chart-wide mb-3",
          div(class = "card-header", textOutput("trendTitle", inline = TRUE)),
          div(class = "card-body",
              plotOutput("trend", height = "440px"))),
      div(class = "card chart-wide mb-3",
          div(class = "card-header", textOutput("balanceTitle", inline = TRUE)),
          div(class = "card-body",
              plotOutput("balance", height = "440px")))
    ),
    
    bslib::nav_panel(
      title = tab_label("02", lbl$tabs$adapt), value = "adapt",
      p(class = "intro", lbl$adaptIntro),
      div(class = "context-banner",
          bsicons::bs_icon("info-circle"),
          textOutput("adaptContext", inline = TRUE)),
      stressCard()
    ),
    
    bslib::nav_panel(
      title = tab_label("03", lbl$tabs$method), value = "method",
      div(class = "section-title",
          span(class = "num", "—"),
          span(lbl$careTitle)),
      div(class = "care-grid",
          purrr::imap(cfg$care, function(b, i) {
            div(class = "care-card",
                tags$span(class = "num", sprintf("%02d", i)),
                h6(b$title),
                p(b$text))
          })
      ),
      div(class = "app-footer", lbl$footer)
    )
  )
)

# 8. SERVEUR ------------------------------------------------------------------

server <- function(input, output, session) {
  
  rv <- reactiveValues(product = NULL)
  
  observeEvent(input$basketClick, {
    req(input$basketClick %in% names(baskets))
    updateSelectInput(session, "basket", selected = input$basketClick)
  })
  
  observeEvent(input$basket, {
    rv$product <- NULL
  }, ignoreInit = TRUE)
  
  basketId <- reactive({
    b <- req(input$basket)
    validate(need(b %in% names(baskets), lbl$errors$noData))
    b
  })
  basket <- reactive(baskets[[basketId()]])
  flow <- reactive({
    f <- flows[[req(input$flow)]]
    validate(need(!is.null(f), lbl$errors$noData))
    f
  })
  flowCode <- reactive(flow()$code)
  year <- reactive({
    y <- as.integer(req(input$year))
    validate(need(y %in% years, lbl$errors$year))
    y
  })
  hubsExcluded <- reactive(isTRUE(input$hubs))
  currentCodes <- reactive({
    if (is.null(rv$product)) names(basket()$products) else rv$product
  })
  currentLabel <- reactive({
    if (is.null(rv$product)) basket()$label else unname(productLabels[rv$product])
  })
  currentMetrics <- reactive({
    computeMetrics(trade, currentCodes(), flowCode(), year(), hubsExcluded())
  })
  
  output$adaptContext <- renderText({
    sprintf(lbl$adaptContext, flow()$label, currentLabel())
  })
  
  # --- Jauges ----------------------------------------------------------------
  output$gaugeTitle <- renderText(sprintf(lbl$gaugeTitle, flow()$partners))
  output$gauges <- renderUI({
    fl <- flowCode(); yr <- year(); hx <- hubsExcluded()
    cards <- purrr::imap(baskets, function(b, id) {
      m <- computeMetrics(trade, names(b$products), fl, yr, hx)
      idx <- match(id, names(baskets))
      makeGauge(id, b$label, m, active = identical(id, basketId()), idx = idx)
    })
    div(class = "gaugeStrip", unname(cards))
  })
  
  # --- Carte -----------------------------------------------------------------
  output$mapTitle <- renderText(sprintf(flow()$mapTitle, tolower(currentLabel())))
  output$mapCrumb <- renderText({
    paste0(basket()$label,
           if (!is.null(rv$product)) paste0(" › HS ", rv$product), " · ", year())
  })
  output$map <- renderPlot({
    plotMap(world, currentMetrics()$shares, input$mapView, hubsExcluded())
  }, res = 96)
  
  # --- Drill-down : produits -------------------------------------------------
  output$drillTitle <- renderText({
    sprintf("%s · %d chapitre(s) HS2", basket()$label, length(basket()$products))
  })
  
  prodTable <- reactive({
    fl <- flowCode(); yr <- year(); hx <- hubsExcluded()
    rows <- purrr::imap(basket()$products, function(label, code) {
      m <- computeMetrics(trade, code, fl, yr, hx)
      data.table(code = code, label = label, total = m$total, hhi = m$hhi,
                 ext = m$ext, level = getLevel(m$hhi)$label)
    }) |> rbindlist()
    setorder(rows, -total)
    if (nrow(rows) > 1L) {
      mAll <- computeMetrics(trade, names(basket()$products), fl, yr, hx)
      rows <- rbind(
        data.table(code = NA_character_, label = lbl$wholeBasket,
                   total = mAll$total, hhi = mAll$hhi, ext = mAll$ext,
                   level = getLevel(mAll$hhi)$label),
        rows)
    }
    rows
  })
  
  output$prodTable <- DT::renderDT({
    dt <- prodTable()
    current <- isolate(rv$product)
    sel <- if (is.null(current)) 1L else match(current, dt$code)
    if (is.na(sel)) sel <- 1L
    display <- dt[, .(
      label = ifelse(is.na(code), label, paste0(label, " (HS ", code, ")")),
      value = total / 1e6, hhi, level, ext)]
    setnames(display, lbl$prodCols)
    DT::datatable(display, rownames = FALSE,
                  selection = list(mode = "single", selected = sel, target = "row"),
                  options = list(dom = "t", paging = FALSE, ordering = FALSE,
                                 scrollY = "300px", scrollCollapse = TRUE)) |>
      DT::formatRound(lbl$prodCols[2], digits = 1, mark = "\u202f", dec.mark = ",") |>
      DT::formatRound(lbl$prodCols[3], digits = 0, mark = "\u202f", dec.mark = ",") |>
      DT::formatPercentage(lbl$prodCols[5], digits = 0, mark = "\u202f", dec.mark = ",")
  })
  
  observeEvent(input$prodTable_rows_selected, {
    dt <- prodTable()
    r <- input$prodTable_rows_selected
    req(length(r) == 1L, r <= nrow(dt))
    code <- dt$code[r]
    newProduct <- if (is.na(code) || length(basket()$products) == 1L) NULL else code
    if (!identical(rv$product, newProduct)) rv$product <- newProduct
  })
  
  # --- Drill-down : partenaires ---------------------------------------------
  output$partnerFor <- renderText({
    paste0(lbl$partnerTitle, " · ", currentLabel(),
           if (hubsExcluded()) lbl$hubsExcludedSuffix else "")
  })
  output$partnerTable <- DT::renderDT({
    top <- head(currentMetrics()$shares, cfg$topPartners)
    validate(need(nrow(top) > 0L, lbl$errors$noData))
    euSet <- euByYear[[as.character(year())]]
    display <- top[, .(
      partnerLabel(partner), share, value / 1e6,
      ifelse(partner %chin% euSet, lbl$blocEu, lbl$blocExtra))]
    setnames(display, lbl$partnerCols)
    DT::datatable(display, rownames = FALSE, selection = "none",
                  options = list(dom = "t", paging = FALSE, ordering = FALSE)) |>
      DT::formatPercentage(lbl$partnerCols[2], digits = 1, mark = "\u202f", dec.mark = ",") |>
      DT::formatRound(lbl$partnerCols[3], digits = 1, mark = "\u202f", dec.mark = ",")
  })
  
  # --- Tendance : HHI annuel -------------------------------------------------
  trendSeries <- reactive({
    codes <- currentCodes(); fl <- flowCode(); hx <- hubsExcluded()
    sub <- trade[.(fl), nomatch = NULL][product %chin% codes]
    setkey(sub, flow, year)
    purrr::map(years, function(y) {
      m <- computeMetrics(sub, codes, fl, y, hx)
      data.table(year = y, hhi = m$hhi, ext = m$ext)
    }) |> rbindlist()
  })
  output$trendTitle <- renderText({
    sprintf(lbl$trendTitle, currentLabel(), flow()$partners, firstYear)
  })
  output$trend <- renderPlot({
    plotTrend(trendSeries(), validEvents)
  }, res = 96)
  
  # --- Importations vs exportations -----------------------------------------
  output$balanceTitle <- renderText(sprintf(lbl$balanceTitle, currentLabel()))
  output$balance <- renderPlot({
    codes <- currentCodes()
    dt <- purrr::imap(flows, function(f, key) {
      totals <- seriesTotals(trade, codes, f$code)
      data.table(flowKey = key, year = years, value = unname(totals) / 1e6)
    }) |> rbindlist()
    plotBalance(dt[value > 0])
  }, res = 96)
  
  # --- Test de stress --------------------------------------------------------
  stress <- reactive({
    ev <- validEvents[[req(input$event)]]
    y0 <- ev$year
    fl <- flowCode(); codes <- currentCodes(); hx <- hubsExcluded()
    yPre  <- y0 - 1L
    yPost <- min(lastYear, y0 + cfg$stress$postOffset)
    yFrom <- max(firstYear + 1L, y0 - cfg$stress$yearsBefore)
    yTo   <- min(lastYear, y0 + cfg$stress$yearsAfter)
    
    totals <- seriesTotals(trade, codes, fl)
    yrs <- yFrom:yTo
    prev <- totals[as.character(yrs - 1L)]
    cur  <- totals[as.character(yrs)]
    yoy <- data.table(year = yrs, change = ifelse(prev > 0, cur / prev - 1, NA_real_))
    
    postRows <- yoy[year >= y0 & is.finite(change)]
    list(ev = ev, y0 = y0, yPre = yPre, yPost = yPost, yoy = yoy,
         changeAtEvent = yoy[year == y0, change],
         pre  = computeMetrics(trade, codes, fl, yPre, hx),
         post = computeMetrics(trade, codes, fl, yPost, hx),
         weakest = if (nrow(postRows) > 0L) postRows[which.min(change)] else NULL)
  })
  
  output$evNote <- renderText({
    s <- stress()
    paste(s$ev$note, sprintf(lbl$stressNote, s$yPost))
  })
  
  output$stKpis <- renderUI({
    s <- stress()
    weakestTxt <- if (is.null(s$weakest)) "–" else
      paste(s$weakest$year, fmtSigned(s$weakest$change, 0))
    div(class = "kpiRow",
        kpiCard(sprintf(lbl$kpi$change, s$y0, s$yPre),
                fmtSigned(s$changeAtEvent, 1)),
        kpiCard(sprintf(lbl$kpi$hhi, s$yPre, s$yPost),
                paste(fmtHhi(s$pre$hhi), "→", fmtHhi(s$post$hhi))),
        kpiCard(sprintf(lbl$kpi$weakest, s$y0), weakestTxt))
  })
  
  output$stChart <- renderPlot({
    s <- stress()
    plotStress(s$yoy, s$y0)
  }, res = 96)
  
  output$shiftTitle <- renderText({
    s <- stress()
    sprintf(lbl$shiftTitle, flow()$partners, s$yPre, s$yPost)
  })
  output$shiftTable <- DT::renderDT({
    s <- stress()
    keys <- union(head(s$pre$shares$partner, cfg$shiftCandidates),
                  head(s$post$shares$partner, cfg$shiftCandidates))
    validate(need(length(keys) > 0L, lbl$errors$noData))
    shift <- data.table(partner = keys)
    shift[, `:=`(
      before = fcoalesce(s$pre$shares$share[match(partner, s$pre$shares$partner)], 0),
      after  = fcoalesce(s$post$shares$share[match(partner, s$post$shares$partner)], 0))]
    shift[, delta := (after - before) * 100]
    shift <- head(shift[order(-abs(delta))], cfg$shiftShown)
    display <- shift[, .(partnerLabel(partner), before, after, delta)]
    setnames(display, lbl$shiftCols)
    DT::datatable(display, rownames = FALSE, selection = "none",
                  options = list(dom = "t", paging = FALSE, ordering = FALSE)) |>
      DT::formatPercentage(lbl$shiftCols[2:3], digits = 1, mark = "\u202f", dec.mark = ",") |>
      DT::formatRound(lbl$shiftCols[4], digits = 1, dec.mark = ",") |>
      DT::formatStyle(lbl$shiftCols[4],
                      color = DT::styleInterval(0, c(cfg$colours$negative,
                                                     cfg$colours$positive)))
  })
}

shinyApp(ui, server)