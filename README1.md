# Sustainable-Livability-SLI – Reproducible Code Guide

This repository contains the **Sustainable Livability Index (SLI)** code and materials.
It shows how to compute SLI from indicators of **Human Actions (HA)**, **Environmental Reactions (ER)**, and **Psychosocial Outcomes (PO)** using **SEM** in Python (`semopy`) and R (`lavaan`).

- Author: **Ramin Gozarani Eghtesad** · ORCID: 0009-0002-8667-8738  
- Contact: ramineqtesad@gmail.com  
- Preprint: SSRN (Abstract ID 5422070)

---

## 1) Repository layout


> **Tip:** GitHub پوشه‌ی خالی را نگه نمی‌دارد. اگر داخل `code/` زیرپوشه می‌سازید (مثلاً `code/data/`)، یک فایل خالی مثل `.gitkeep` بگذارید.

---

## 2) Data input

Put your CSV in a path you like (e.g., `code/data/toy_sli_data.csv`) with columns like:

- **HA**: `water_extraction`, `dam_density`, `well_density`  
- **ER**: `soil_electrical_cond`, `ndvi_decline`, `dust_storm_freq`  
- **PO**: `climate_anxiety`, `migration_intent`, `place_attachment_loss`

The scripts do **min–max normalization** and compute block scores.

---

## 3) Python pipeline (semopy)

### 3.1. Install
```bash
pip install semopy pandas numpy scikit-learn
3.2. Run with equal weights
python code/code.SLM.SEM.py
3.3. Run with PW/EW/HW weights
First, adjust weights_example.json if needed; then:
# Policy-weight run
python code/code.SLM.SEM.py --scheme PW --weights ./weights_example.json

# Empirical-weight run
python code/code.SLM.SEM.py --scheme EW --weights ./weights_example.json

# Hybrid-weight run
python code/code.SLM.SEM.py --scheme HW --weights ./weights_example.json
Outputs (in repo root):

results_semopy_params.csv – parameters & loadings
results_semopy_fit.csv – fit indices (CFI, RMSEA, …)
results_sli_values.csv – HA/ER/PO scores + SLI_simple
4) R pipeline (lavaan)
4.1. Install
install.packages(c("lavaan","readr","dplyr"))
4.2. Run with equal weights
source("code/code.SEM.Lavan.R")
4.3. Run with PW/EW/HW weights
# from terminal
Rscript code/code.SEM.Lavan.R --scheme=PW --weights=./weights_example.json
Rscript code/code.SEM.Lavan.R --scheme=EW --weights=./weights_example.json
Rscript code/code.SEM.Lavan.R --scheme=HW --weights=./weights_example.json
Outputs (in repo root):

results_lavaan_params.csv – standardized paths
results_lavaan_fit.csv – fit indices
results_sli_values_r.csv – block scores + SLI_simple
5) Blend PW/EW/HW to final SLI (0.3 / 0.4 / 0.3)
After you have three runs (PW, EW, HW), combine them:
python combine_schemes.py \
  --pw path/to/PW/results_sli_values.csv \
  --ew path/to/EW/results_sli_values.csv \
  --hw path/to/HW/results_sli_values.csv \
  --out blended_sli.csv
This creates blended_sli.csv with SLI_blended = 0.3*PW + 0.4*EW + 0.3*HW.
Recommendation: To avoid overwriting, run each scheme in a separate folder (e.g., runs/PW/, runs/EW/, runs/HW/) and pass the three paths to the combiner.
6) Reproducibility notes
Random seeds are fixed by default through deterministic operations; if you add stochastic steps, set seeds.
Replace the toy/example data with your Urmia/Hawizeh regional data to reproduce the manuscript’s results.
Cite this repository and SSRN entry when using the code.
7) Citation
If you use this repository:
Gozarani Eghtesad, R. (2025). Sustainable Livability Index (SLI): Code and Replication Materials. SSRN Abstract ID 5422070.
Repository: https://github.com/ramineqtesad/Sustainable-Livability-SLI
Licenses: Code under MIT; text/data under CC BY 4.0.
