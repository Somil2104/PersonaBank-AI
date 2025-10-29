import pandas as pd

df = pd.read_csv("customer_features_min.csv")
cats = [c for c in ['groceries','food','apparel','retail','travel','utilities','other'] if c in df.columns]

def dom_cat(row):
    if not cats: return 'other'
    sub = row[cats]
    if sub.sum() == 0: return 'other'
    return sub.idxmax()

def freq_band(v):
    if v >= 20: return 'Very-High'
    if v >= 10: return 'High'
    if v >= 4:  return 'Medium'
    if v >= 1:  return 'Low'
    return 'Very-Low'

def value_band(v):
    if v >= 200: return 'High-Ticket'
    if v >= 75:  return 'Mid-Ticket'
    return 'Low-Ticket'

def pseudo_label(row):
    dc = row['dom_cat']
    fb = row['freq_band']
    vb = row['value_band']
    if dc in ['groceries','food'] and fb in ['High','Very-High']:
        return 'Everyday Spender'
    if dc in ['retail','apparel'] and row.get('online_share',0.0) >= 0.5:
        return 'Online Shopper'
    if dc == 'travel' and vb == 'High-Ticket':
        return 'Traveler/High-Value'
    if dc == 'utilities' and fb in ['Medium','High','Very-High']:
        return 'Bills/Utilities'
    if vb == 'High-Ticket' and fb in ['Low','Very-Low']:
        return 'Occasional Big-Spender'
    return 'Mixed/General'

def offers(label):
    if label == 'Everyday Spender':
        return ['Grocery & dining cashback', 'BNPL for essentials', 'Bill-pay rewards']
    if label == 'Online Shopper':
        return ['Online rewards card', 'Virtual card offers', 'Marketplace cashback']
    if label == 'Traveler/High-Value':
        return ['Travel card FX waiver', 'Lounge access', 'EMI for large purchases']
    if label == 'Bills/Utilities':
        return ['Autopay rewards', 'Utility bill cashback', 'Budgeting insights']
    if label == 'Occasional Big-Spender':
        return ['Low-interest EMI', 'High-limit review', 'Category boost on large spends']
    return ['General cashback card', 'Savings booster']

df['dom_cat'] = df.apply(dom_cat, axis=1)
df['freq_band'] = df['tx_per_month'].apply(freq_band)
df['value_band'] = df['amt_mean'].apply(value_band)
df['pseudo_cluster'] = df.apply(pseudo_label, axis=1)

cl = df[['customer_id','pseudo_cluster','dom_cat','freq_band','value_band']]
cl.to_csv("customer_pseudo_clusters.csv", index=False)
rec = cl.copy()
rec['offers'] = rec['pseudo_cluster'].apply(lambda L: '; '.join(offers(L)))
rec['risk_band'] = 'Med'  # placeholder PD
rec.to_csv("customer_recommendations_pseudo.csv", index=False)
print("Wrote customer_pseudo_clusters.csv and customer_recommendations_pseudo.csv")
