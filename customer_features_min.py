import pandas as pd, numpy as np

tx = pd.read_csv("transactions_unified_altman.csv", parse_dates=['event_time'])
tx['customer_id'] = tx['customer_id'].astype(str)

def map_cat(mcc):
    s = str(mcc)
    # Exact/common MCCs
    if s.startswith('5411'): return 'groceries'
    if s.startswith('5812') or s.startswith('5814'): return 'food'
    if s.startswith('5651'): return 'apparel'
    if s.startswith('5999') or s.startswith('5970') or s.startswith('594'): return 'retail'
    if s.startswith('3000') or s.startswith('3011') or s.startswith('4411') or s.startswith('4511') or s.startswith('4112'): return 'travel'
    if s.startswith('4812') or s.startswith('4821') or s.startswith('4899'): return 'utilities'
    if s.startswith('5912'): return 'pharmacy'
    if s.startswith('5300'): return 'wholesale'
    # Broad fallbacks
    if s.startswith('58'): return 'food'
    if s.startswith('56'): return 'apparel'
    if s.startswith('59'): return 'retail'
    if s.startswith('41') or s.startswith('30') or s.startswith('40'): return 'travel'
    if s.startswith('48'): return 'utilities'
    return 'other'


tx['cat'] = tx['mcc'].apply(map_cat)

# Category spend shares
pivot = tx.pivot_table(index='customer_id', columns='cat', values='amount', aggfunc='sum', fill_value=0.0)
pivot['total_spend'] = pivot.sum(axis=1)
for c in pivot.columns:
    if c != 'total_spend':
        pivot[c] = pivot[c] / pivot['total_spend'].replace(0, 1.0)

# Frequency and ticket size
tx['month'] = tx['event_time'].dt.to_period('M')
g = tx.groupby('customer_id')
feat = pd.DataFrame({
    'tx_count': g.size(),
    'months': g['month'].nunique(),
    'amt_mean': g['amount'].mean(),
}).fillna(0.0)
feat['tx_per_month'] = feat['tx_count'] / feat['months'].replace(0, np.nan)
feat['tx_per_month'] = feat['tx_per_month'].fillna(0.0)

# Online share (optional)
chan = tx.pivot_table(index='customer_id', columns='channel', values='amount', aggfunc='sum', fill_value=0.0)
for c in ['online','pos']:
    if c not in chan.columns: chan[c] = 0.0
chan['online_share'] = chan['online'] / (chan['online'] + chan['pos']).replace(0, np.nan)
chan['online_share'] = chan['online_share'].fillna(0.0)

out = pivot.drop(columns=['total_spend']).join(feat[['tx_count','tx_per_month','amt_mean']], how='left')
out = out.join(chan[['online_share']], how='left').fillna(0.0)
out.reset_index().to_csv("customer_features_min.csv", index=False)
print("Wrote customer_features_min.csv", out.shape)
