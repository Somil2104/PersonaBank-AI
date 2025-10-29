import pandas as pd

features = pd.read_csv("customer_features_altman.csv")
clusters = pd.read_csv("customer_clusters_altman.csv")

cat_cols = [c for c in ['groceries','food','apparel','retail','travel','utilities','pharmacy','wholesale','other'] if c in features.columns]
for c in ['tx_per_month','amt_mean','online_share']:
    if c not in features.columns:
        features[c] = 0.0

def dom_cat(row):
    if not cat_cols:
        return 'other'
    sub = row[cat_cols]
    if sub.fillna(0).sum() <= 0:
        return 'other'
    return sub.idxmax()

def freq_band(v):
    return 'Very-High' if v >= 12 else 'High' if v >= 6 else 'Medium' if v >= 3 else 'Low' if v >= 1 else 'Very-Low'

def value_band(v):
    return 'High-Ticket' if v >= 300 else 'Mid-Ticket' if v >= 75 else 'Low-Ticket'

def label_from_signals(dc, fb, vb, online_share):
    if dc in ['groceries','food'] and fb in ['High','Very-High']: return 'Everyday Spender'
    if dc in ['retail','apparel'] and online_share >= 0.5:         return 'Online Shopper'
    if dc == 'travel' and vb == 'High-Ticket':                      return 'Traveler/High-Value'
    if dc == 'utilities' and fb in ['Medium','High','Very-High']:   return 'Bills/Utilities'
    if vb == 'High-Ticket' and fb in ['Very-Low','Low']:            return 'Occasional Big-Spender'
    return 'Mixed'

def offers(label):
    return {
        'Everyday Spender': 'Grocery & dining cashback; BNPL for essentials; Bill-pay rewards',
        'Online Shopper': 'Online rewards card; Virtual card offers; Marketplace cashback',
        'Traveler/High-Value': 'Travel card FX waiver; Lounge access; EMI for large purchases',
        'Bills/Utilities': 'Autopay rewards; Utility bill cashback; Budgeting insights',
        'Occasional Big-Spender': 'Low-interest EMI; High-limit review; Category boost on large spends',
        'Mixed': 'General cashback card; Savings booster'
    }.get(label, 'General cashback card; Savings booster')

df = features.merge(clusters, on='customer_id', how='inner').copy()
df['dom_cat'] = df.apply(dom_cat, axis=1)
df['freq_band'] = df['tx_per_month'].apply(freq_band)
df['value_band'] = df['amt_mean'].apply(value_band)
df['cluster_label'] = df.apply(lambda r: label_from_signals(r['dom_cat'], r['freq_band'], r['value_band'], r.get('online_share',0.0)), axis=1)
df['offers'] = df['cluster_label'].apply(offers)
df['risk_band'] = 'Med'

out = df[['customer_id','cluster','cluster_label','dom_cat','freq_band','value_band','offers','risk_band']]
out.to_csv("customer_recommendations_altman.csv", index=False)
print("Wrote customer_recommendations_altman.csv", out.shape)
