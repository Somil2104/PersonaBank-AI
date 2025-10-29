import os, subprocess, sys, json
import pandas as pd

# Demo-friendly thresholds (restore to 50 and 0.15 later)
N_MIN_FOR_CLUSTERING = 3
SIL_MIN = 0.0

def run(cmd: str):
    print("+", cmd)
    rc = subprocess.call(cmd, shell=True)
    if rc != 0:
        sys.exit(rc)

def count_customers(path: str) -> int:
    df = pd.read_csv(path)
    return df['customer_id'].nunique()

# 1) Always compute features (prefer rich features if available)
if os.path.exists("transactions_unified_altman.csv"):
    rc = subprocess.call("python3 customer_features_altman.py", shell=True)
    if rc != 0 or not os.path.exists("customer_features_altman.csv"):
        run("python3 customer_features_min.py")
    feat_path = "customer_features_altman.csv" if os.path.exists("customer_features_altman.csv") else "customer_features_min.csv"
else:
    run("python3 customer_features_min.py")
    feat_path = "customer_features_min.csv"

# 2) Choose segmentation path based on customer count
n = count_customers(feat_path)
print(f"Unique customers: {n}")

if n < N_MIN_FOR_CLUSTERING:
    print(f"Using pseudo rules (n < {N_MIN_FOR_CLUSTERING})")
    run("python3 pseudo_cluster_and_recommend.py")
    run("cp -f customer_recommendations_pseudo.csv customer_recommendations.csv")
else:
    print("Using KMeans clustering")
    run("python3 cluster_customers_altman.py")
    # Quality gate: fall back to rules if silhouette too low (disabled for demo with SIL_MIN=0.0)
    try:
        meta = json.load(open("customer_clusters_meta_altman.json"))
        sil = meta.get("silhouette", None)
    except Exception:
        sil = None

    if sil is None or (isinstance(sil, (int, float)) and sil < SIL_MIN):
        print(f"Silhouette {sil} below {SIL_MIN}; falling back to pseudo rules")
        run("python3 pseudo_cluster_and_recommend.py")
        run("cp -f customer_recommendations_pseudo.csv customer_recommendations.csv")
    else:
        run("python3 recommend_offers_altman.py")
        run("cp -f customer_recommendations_altman.csv customer_recommendations.csv")

# 3) Pretty print summary for demo
out = pd.read_csv("customer_recommendations.csv")
for _, r in out.iterrows():
    cid = r['customer_id']
    seg = r.get('cluster_label', r.get('pseudo_cluster', 'Unknown'))
    offers = r.get('offers', '')
    risk = r.get('risk_band', 'NA')
    print(f"[Segmentation] customer_id={cid} | segment={seg} | risk={risk} | offers={offers}")

print("Segmentation ready at customer_recommendations.csv")
