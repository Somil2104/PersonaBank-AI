import json, numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score

df = pd.read_csv("customer_features_altman.csv")
if df.shape[0] < 2:
    # Not enough customers to cluster
    df[['customer_id']].assign(cluster=0).to_csv("customer_clusters_altman.csv", index=False)
    meta = {
        'k': 1, 'silhouette': None, 'feature_cols': [c for c in df.columns if c!='customer_id'],
        'topcats': {0: {'top5': []}}, 'note': 'only one customer; assigned to cluster 0'
    }
    with open("customer_clusters_meta_altman.json","w") as f:
        json.dump(meta, f, indent=2)
    print("Only one customer found; assigned cluster 0.")
    raise SystemExit(0)

cust = df['customer_id'].values
feat_cols = [c for c in df.columns if c != 'customer_id']
X = df[feat_cols].values

scaler = StandardScaler()
Xs = scaler.fit_transform(X)

n = df.shape[0]
k_min, k_max = 2, min(12, n)  # k cannot exceed n
best = None
for k in range(k_min, k_max + 1):
    km = MiniBatchKMeans(n_clusters=k, random_state=42, batch_size=min(4096, max(256, n*4)), n_init='auto')
    labels = km.fit_predict(Xs)
    score = silhouette_score(Xs, labels) if k < n else None
    if (best is None) or (score is not None and score > best['score']):
        best = {'k': k, 'labels': labels, 'score': float(score) if score is not None else None}

print("Selected k:", best['k'], "silhouette:", best['score'])
pd.DataFrame({'customer_id': cust, 'cluster': best['labels']}).to_csv("customer_clusters_altman.csv", index=False)

top = {}
for cidx in np.unique(best['labels']):
    mean_vec = df.loc[best['labels']==cidx, feat_cols].mean().sort_values(ascending=False)
    top[int(cidx)] = {'top5': mean_vec.head(5).index.tolist()}
meta = {'k': best['k'], 'silhouette': best['score'], 'feature_cols': feat_cols, 'topcats': top,
        'scaler_mean': scaler.mean_.tolist(), 'scaler_var': scaler.var_.tolist()}
with open("customer_clusters_meta_altman.json","w") as f:
    json.dump(meta, f, indent=2)
print("Wrote customer_clusters_altman.csv and customer_clusters_meta_altman.json")
