# combine_schemes.py
# ------------------------------------------------------------
# Combine SLI results from PW, EW, HW runs into a blended SLI:
# SLI_blended = 0.3*SLI_PW + 0.4*SLI_EW + 0.3*SLI_HW
# Each input CSV must have columns: HA_score, ER_score, PO_score, SLI_simple
# ------------------------------------------------------------

import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--pw", required=True, help="Path to PW results_sli_values.csv")
parser.add_argument("--ew", required=True, help="Path to EW results_sli_values.csv")
parser.add_argument("--hw", required=True, help="Path to HW results_sli_values.csv")
parser.add_argument("--out", default="blended_sli.csv", help="Output CSV filename")
args = parser.parse_args()

pw = pd.read_csv(args.pw)
ew = pd.read_csv(args.ew)
hw = pd.read_csv(args.hw)

# sanity checks
for df in (pw, ew, hw):
    assert {"HA_score","ER_score","PO_score","SLI_simple"}.issubset(df.columns), \
        "Input CSV must have HA_score, ER_score, PO_score, SLI_simple"

blended = pd.DataFrame({
    "HA_score_blend": 0.3*pw["HA_score"] + 0.4*ew["HA_score"] + 0.3*hw["HA_score"],
    "ER_score_blend": 0.3*pw["ER_score"] + 0.4*ew["ER_score"] + 0.3*hw["ER_score"],
    "PO_score_blend": 0.3*pw["PO_score"] + 0.4*ew["PO_score"] + 0.3*hw["PO_score"],
    "SLI_blended":    0.3*pw["SLI_simple"] + 0.4*ew["SLI_simple"] + 0.3*hw["SLI_simple"]
})
blended.to_csv(args.out, index=False)
print("Saved:", args.out)
