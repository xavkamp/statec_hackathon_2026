# =============================================================================
# prepareData.R
# Lit le CSV Comext (SDMX-CSV étiqueté, annuel, HS2, import + export) et
# produit data/resilienceData.rds pour l'application.
# =============================================================================

library(data.table)
library(purrr)

# Configuration : aucun chemin, code ou nom de colonne en dur plus bas ---------
cfgPrep <- list(
  csvPaths    = "shinyApp/data/comext_LU_hs2_all.csv",                  # un ou plusieurs fichiers
  outPath     = file.path("shinyApp/data", "resilienceData.rds"),
  reporter    = "LU",
  indicator   = "VALUE_IN_EUROS",
  freq        = "A",
  # Colonnes lues en texte (sinon le chapitre "01" devient 1)
  charCols    = c("freq", "reporter", "partner", "partner_label", "product",
                  "product_label", "flow", "indicators", "time"),
  numCols     = "value",
  partnerPattern = "^[A-Z]{2}$",                  # écarte les agrégats (EU27_2020...)
  productPattern = "^[0-9]{2}$",                  # chapitres HS2 uniquement
  # Partenaires "non spécifiés" : codes connus + motif sur le libellé
  unspecifiedCodes   = c("XX", "QP", "QQ", "QR", "QS", "QU", "QV", "QW", "QX",
                         "QY", "QZ"),
  unspecifiedPattern = "not specified|unspecified|secret|confidential|stores|provisions|not determined",
  # Contrôles de complétude (avertissements, pas d'arrêt)
  minProducts = 10L,
  lastLetterExpected = "W"      # des partenaires jusqu'à "W..." doivent exister
)

#' Lit un CSV Comext en contrôlant les types
#'
#' na.strings = "" : sinon fread() lirait le code partenaire "NA" (Namibie)
#' comme une valeur manquante.
readComextCsv <- function(path) {
  if (!file.exists(path)) stop("Fichier introuvable : ", path, call. = FALSE)
  dt <- fread(path, colClasses = list(character = cfgPrep$charCols),
              na.strings = "", encoding = "UTF-8")
  needed <- c(cfgPrep$charCols, cfgPrep$numCols)
  missingCols <- setdiff(needed, names(dt))
  if (length(missingCols) > 0L) {
    stop("Colonnes absentes de ", path, " : ",
         paste(missingCols, collapse = ", "), call. = FALSE)
  }
  dt[, needed, with = FALSE]
}

#' "LIVE ANIMALS" -> "Live animals"
sentenceCase <- function(x) {
  x <- tolower(x)
  paste0(toupper(substr(x, 1, 1)), substring(x, 2))
}

# 1. Lecture et filtres --------------------------------------------------------
raw <- purrr::map(cfgPrep$csvPaths, readComextCsv) |>
  rbindlist(use.names = TRUE) |>
  unique()                                        # fichiers qui se chevauchent

nBefore <- nrow(raw)
raw <- raw[reporter == cfgPrep$reporter & indicators == cfgPrep$indicator &
             freq == cfgPrep$freq & !is.na(value)]
if (nrow(raw) == 0L) {
  stop("Aucune ligne après filtre déclarant/indicateur/fréquence (",
       nBefore, " lignes lues).", call. = FALSE)
}

# 2. Partenaires et produits : on ne garde que pays et chapitres HS2 -----------
droppedPartners <- unique(raw[!grepl(cfgPrep$partnerPattern, partner), partner])
if (length(droppedPartners) > 0L) {
  message("Partenaires écartés (agrégats) : ", paste(droppedPartners, collapse = ", "))
}
raw <- raw[grepl(cfgPrep$partnerPattern, partner) &
             grepl(cfgPrep$productPattern, product)]
raw[, year := as.integer(time)]
stopifnot(!anyNA(raw$year), nrow(raw) > 0L)

# 3. Dictionnaires -------------------------------------------------------------
partnersDt <- unique(raw[, .(partner, partner_label)], by = "partner")
productsDt <- unique(raw[, .(product, product_label)], by = "product")
unspecified <- union(
  intersect(cfgPrep$unspecifiedCodes, partnersDt$partner),
  partnersDt[grepl(cfgPrep$unspecifiedPattern, partner_label, ignore.case = TRUE),
             partner])

# 4. Agrégation finale ---------------------------------------------------------
trade <- raw[, .(value = sum(value)), by = .(flow, product, partner, year)]
trade <- trade[value != 0]

# 5. Contrôles de complétude ---------------------------------------------------
if (uniqueN(trade$product) < cfgPrep$minProducts) {
  warning("Seulement ", uniqueN(trade$product), " chapitre(s) HS2 : ",
          "extraction probablement incomplète.", call. = FALSE)
}
lastPartner <- max(trade$partner)
if (lastPartner < cfgPrep$lastLetterExpected) {
  warning("Les partenaires s'arrêtent à '", lastPartner, "' : ",
          "extraction probablement tronquée (413 / erreurs silencieuses ?).",
          call. = FALSE)
}

# 6. Sauvegarde ----------------------------------------------------------------
dataStore <- list(
  trade       = trade,                            # flow, product, partner, year, value
  years       = seq(min(trade$year), max(trade$year)),
  partners    = setNames(partnersDt$partner_label, partnersDt$partner),
  products    = setNames(sentenceCase(productsDt$product_label), productsDt$product),
  unspecified = unspecified,
  updated     = format(max(file.mtime(cfgPrep$csvPaths)), "%Y-%m-%d")
)
dir.create(dirname(cfgPrep$outPath), showWarnings = FALSE, recursive = TRUE)
saveRDS(dataStore, cfgPrep$outPath)

message(sprintf("OK : %d lignes | %d chapitres | %d partenaires | %d-%d | flux : %s",
                nrow(trade), uniqueN(trade$product), uniqueN(trade$partner),
                min(trade$year), max(trade$year),
                paste(sort(unique(trade$flow)), collapse = ", ")))
message("Partenaires non spécifiés détectés : ",
        if (length(unspecified) > 0L) paste(unspecified, collapse = ", ") else "aucun")
