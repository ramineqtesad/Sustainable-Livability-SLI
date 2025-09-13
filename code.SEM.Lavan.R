# SLI_SEM_lavaan.R
# ------------------------------------------------------------
# R implementation of the SLI pipeline using lavaan.
# Steps: read data -> min-max normalize -> compute block scores
# -> specify CFA/SEM (HA, ER, PO) -> fit -> print/export results.
# ------------------------------------------------------------

# install.packages(c("lavaan","readr","dplyr"), dependencies = TRUE)
suppressPackageStartupMessages({
  library(lavaan)
  library(readr)
  library(dplyr)
})

# ------------------------------------------------------------
# 1) Load data
# ------------------------------------------------------------
data_path <- file.path(dirname(sys.frame(1)$ofile %||% "."), "..", "data", "toy_sli_data.csv")
df <- read_csv(data_path, show_col_types = FALSE)

ha_vars <- c("water_extraction","dam_density","well_density")
er_vars <- c("soil_electrical_cond","ndvi_decline","dust_storm_freq")
po_vars <- c("climate_anxiety","migration_intent","place_attachment_loss")

# ------------------------------------------------------------
# 2) Min–max normalization
# ------------------------------------------------------------
minmax <- function(x) {
  rng <- range(x, na.rm = TRUE)
  if (diff(rng) == 0) return(rep(0, length(x)))
  (x - rng[1]) / (rng[2] - rng[1])
}

df_norm <- df
for (v in c(ha_vars, er_vars, po_vars)) {
  df_norm[[v]] <- minmax(df[[v]])
}

# ------------------------------------------------------------
# 3) Block scores (equal weights by default; adapt as needed)
# ------------------------------------------------------------
block_score <- function(dd, vars, w = NULL) {
  if (is.null(w)) w <- rep(1/length(vars), length(vars))
  w <- w / sum(w)
  as.numeric(as.matrix(dd[, vars]) %*% w)
}

df_norm$HA_score <- block_score(df_norm, ha_vars)
df_norm$ER_score <- block_score(df_norm, er_vars)
df_norm$PO_score <- block_score(df_norm, po_vars)
df_norm$SLI_simple <- rowMeans(df_norm[, c("HA_score","ER_score","PO_score")])

# ------------------------------------------------------------
# 4) SEM model (lavaan syntax)
# ------------------------------------------------------------
model <- '
  # Measurement
  HA =~ water_extraction + dam_density + well_density
  ER =~ soil_electrical_cond + ndvi_decline + dust_storm_freq
  PO =~ climate_anxiety + migration_intent + place_attachment_loss

  # Structural
  ER ~ HA
  PO ~ ER + HA
'

fit <- sem(model, data = df_norm, estimator = "MLR")  # robust ML

# ------------------------------------------------------------
# 5) Results: print & export
# ------------------------------------------------------------
summ <- summary(fit, standardized = TRUE, fit.measures = TRUE)
print(summ)

# Extract standardized solution
std_sol <- standardizedSolution(fit)
fit_meas <- fitMeasures(fit, c("npar","chisq","df","pvalue","cfi","tli","rmsea","srmr"))

# Export CSVs next to project root
root_dir <- normalizePath(file.path(dirname(sys.frame(1)$ofile %||% "."), ".."))
write.csv(std_sol, file.path(root_dir, "results_lavaan_params.csv"), row.names = FALSE)
write.csv(as.data.frame(t(fit_meas)), file.path(root_dir, "results_lavaan_fit.csv"), row.names = TRUE)
write.csv(df_norm[, c("HA_score","ER_score","PO_score","SLI_simple")], file.path(root_dir, "results_sli_values_r.csv"), row.names = FALSE)

cat("\nSaved:\n",
    file.path(root_dir, "results_lavaan_params.csv"), "\n",
    file.path(root_dir, "results_lavaan_fit.csv"), "\n",
    file.path(root_dir, "results_sli_values_r.csv"), "\n", sep = "")
