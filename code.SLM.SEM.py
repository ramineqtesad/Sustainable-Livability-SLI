# SLI_SEM_semopy.py  (with PW/EW/HW weighting support)
import os, json, argparse
import pandas as pd, numpy as np
from semopy import Model
from semopy import calc_stats

# --------------------- CLI ---------------------
parser = argparse.ArgumentParser(description="Run SLI SEM with optional weighting scheme.")
parser.add_argument("--scheme", choices=["PW","EW","HW"], default=None,
                    help="Choose in-block weighting scheme (PW/EW/HW). If omitted, equal weights are used.")
parser.add_argument("--weights", default=None,
                    help="Path to weights JSON (e.g., ../weights_example.json).")
args = parser.parse_args()

# --------------------- Data --------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "toy_sli_data.csv")
df = pd.read_csv(DATA_PATH)

ha_vars = ["water_extraction", "dam_density", "well_density"]
er_vars = ["soil_electrical_cond", "ndvi_decline", "dust_storm_freq"]
po_vars = ["climate_anxiety", "migration_intent", "place_attachment_loss"]

def minmax(col: pd.Series) -> pd.Series:
    cmin, cmax = col.min(), col.max()
    return (col - cmin) / (cmax - cmin) if cmax != cmin else pd.Series(np.zeros(len(col)), index=col.index)

df_norm = df.copy()
for col in ha_vars + er_vars + po_vars:
    df_norm[col] = minmax(df[col])

# --------------------- Weights -----------------
def get_weights_from_json(path, scheme):
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    sch = scheme or obj.get("scheme")
    bw = obj["block_weights"][sch]
    return bw["HA"], bw["ER"], bw["PO"]

def block_score(df_block: pd.DataFrame, weights=None):
    n = df_block.shape[1]
    if weights is None:
        weights = np.ones(n) / n
    weights = np.array(weights, dtype=float)
    weights = weights / weights.sum()
    return (df_block.values * weights).sum(axis=1)

ha_w = er_w = po_w = None
if args.weights:
    ha_w, er_w, po_w = get_weights_from_json(args.weights, args.scheme)
elif args.scheme:
    raise SystemExit("If you pass --scheme, please also provide --weights JSON to map scheme to vectors.")

df_norm["HA_score"] = block_score(df_norm[ha_vars], ha_w)
df_norm["ER_score"] = block_score(df_norm[er_vars], er_w)
df_norm["PO_score"] = block_score(df_norm[po_vars], po_w)

# SLI (simple average of latent blocks)
df_norm["SLI_simple"] = df_norm[["HA_score","ER_score","PO_score"]].mean(axis=1)

# OPTIONAL: blended SLI using PW/EW/HW = 0.3/0.4/0.3 when three runs are available.
# For a single run with one scheme, we keep SLI_simple. If you want blended:
#   run three times with --scheme PW/EW/HW and then combine externally.

# --------------------- SEM ---------------------
model_desc = """
HA =~ water_extraction + dam_density + well_density
ER =~ soil_electrical_cond + ndvi_decline + dust_storm_freq
PO =~ climate_anxiety + migration_intent + place_attachment_loss

ER ~ HA
PO ~ ER + HA
"""
model = Model(model_desc)
model.fit(df_norm, obj="MLW")

params = model.inspect()
stats = calc_stats(model)

# --------------------- Export ------------------
root = os.path.join(os.path.dirname(__file__), "..")
params.to_csv(os.path.join(root, "results_semopy_params.csv"), index=False)

fit_df = pd.DataFrame({
    "n_obs": [stats.n_obs],
    "df": [stats.df],
    "chisq": [stats.chi2],
    "p_value": [stats.p_value],
    "cfi": [stats.fit["CFI"]],
    "tli": [stats.fit.get("TLI", np.nan)],
    "rmsea": [stats.fit["RMSEA"]],
    "srmr": [stats.fit.get("SRMR", np.nan)]
})
fit_df.to_csv(os.path.join(root, "results_semopy_fit.csv"), index=False)

df_norm[["HA_score","ER_score","PO_score","SLI_simple"]].to_csv(os.path.join(root, "results_sli_values.csv"), index=False)

print("Done. Scheme:", args.scheme or "equal-weights")

