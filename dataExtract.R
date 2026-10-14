
library(data.table)
library(purrr)

# 1. Dictionnaire de paramètres ------------------------------------------
# Aucune valeur en dur dans le code : tout passe par ce dictionnaire
comextConfig <- list(
  baseUrl = "https://ec.europa.eu/eurostat/api/comext/dissemination/sdmx/2.1/data",
  datasetId = "DS-045409",
  freq = "A", # "A" = annuel, "M" = mensuel
  reporter = "LU", # Luxembourg
  flows = c(import = "1", export = "2"),
  indicators = c("VALUE_IN_EUROS"),
  startPeriod = "2000", # ex. "2000" pour restreindre
  endPeriod = NULL,
  cacheDir = "comextCache"
)

dir.create(comextConfig$cacheDir, showWarnings = FALSE)

# 2. Construction de l'URL ------------------------------------------------
buildComextUrl <- function(partner, flow, indicator, config = comextConfig) {
  # Clé SDMX : freq.reporter.partner.product.flow.indicators
  # (product vide = tous les produits)
  key <- paste(
    config$freq, config$reporter, partner, "", flow, indicator,
    sep = "."
  )
  
  # Paramètres optionnels de période (NULL est ignoré par c())
  params <- c(
    "format=SDMX-CSV",
    if (!is.null(config$startPeriod)) paste0("startPeriod=", config$startPeriod),
    if (!is.null(config$endPeriod)) paste0("endPeriod=", config$endPeriod)
  )
  
  paste0(
    config$baseUrl, "/", config$datasetId, "/", key,
    "?", paste(params, collapse = "&")
  )
}

# 3. Téléchargement d'un bloc (avec cache disque et gestion d'erreur) ----
fetchComextChunk <- function(partner, flow, indicator, config = comextConfig) {
  # Fichier de cache : permet de reprendre après une interruption
  cacheFile <- file.path(
    config$cacheDir,
    paste0(partner, "_", flow, "_", indicator, ".rds")
  )
  if (file.exists(cacheFile)) {
    return(readRDS(cacheFile))
  }
  
  url <- buildComextUrl(partner, flow, indicator, config)
  
  chunk <- tryCatch(
    fread(url, showProgress = FALSE),
    error = function(e) {
      message("Échec : ", partner, " / flux ", flow, " / ", indicator)
      NULL # partenaire sans données (404) ou erreur réseau
    }
  )
  
  # Programmation défensive : on vérifie que la réponse est bien un CSV SDMX
  if (is.null(chunk) || !"OBS_VALUE" %in% names(chunk)) {
    return(NULL)
  }
  
  saveRDS(chunk, cacheFile)
  chunk
}

# 4. Liste des partenaires -----------------------------------------------
partnerTable <- as.data.table(comRex::cr_get_ref_table("partner"))
partnerCodes <- partnerTable[, unique(code)]

# 5. Grille de requêtes et extraction ------------------------------------
queryGrid <- CJ(
  partner = partnerCodes,
  flow = comextConfig$flows,
  indicator = comextConfig$indicators,
  sorted = FALSE
)

# pmap_dfr/pmap + rbindlist : un bloc par ligne de la grille
luxTrade <- queryGrid |>
  pmap(\(partner, flow, indicator) {
    fetchComextChunk(partner, flow, indicator)
  }) |>
  compact() |> # supprime les blocs NULL
  rbindlist(fill = TRUE)

# 6. Contrôles rapides ---------------------------------------------------
stopifnot(nrow(luxTrade) > 0)
luxTrade[, .N, by = .(flow, indicators)]

# 7. Sauvegarde ----------------------------------------------------------
saveRDS(luxTrade, "luxTradeDs045409.rds")
