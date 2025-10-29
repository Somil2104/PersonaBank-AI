import pandas as pd, numpy as np

tx = pd.read_csv("transactions_unified_altman.csv", parse_dates=['event_time'])
ucf = pd.read_csv("user_card_features.csv")
tx['customer_id'] = tx['customer_id'].astype(str)
ucf['user'] = ucf['user'].astype(str)

def map_cat(mcc):
    s = str(mcc)
    if s.startswith('5411'): return 'groceries'
    if s.startswith('5812') or s.startswith('5814'): return 'food'
    if s.startswith('5651'): return 'apparel'
    if s.startswith('5999') or s.startswith('5970') or s.startswith('594'): return 'retail'
    if s.startswith('3000') or s.startswith('3011') or s.startswith('4411') or s.startswith('4511') or s.startswith('4112'): return 'travel'
    if s.startswith('4812') or s.startswith('4821') or s.startswith('4899'): return 'utilities'
    if s.startswith('5912'): return 'pharmacy'
    if s.startswith('5300'): return 'wholesale'
    if s.startswith('58'): return 'food'
    if s.startswith('56'): return 'apparel'
    if s.startswith('59'): return 'retail'
    if s.startswith('41') or s.startswith('30') or s.startswith('40'): return 'travel'
    if s.startswith('48'): return 'utilities'
    return 'other'

tx['cat'] = tx['mcc'].apply(map_cat)

# Category shares
pivot = tx.pivot_table(index='customer_id', columns='cat', values='amount', aggfunc='sum', fill_value=0.0)
pivot['total_spend'] = pivot.sum(axis=1)
for c in pivot.columns:
    if c != 'total_spend':
        pivot[c] = pivot[c] / pivot['total_spend'].replace(0, 1.0)

# Ensure expected category columns exist
cat_cols = ['groceries','food','apparel','retail','travel','utilities','pharmacy','wholesale','other']
for c in cat_cols:
    if c not in pivot.columns:
        pivot[c] = 0.0
pivot = pivot[cat_cols + ['total_spend']]

# Behavior and channel
tx['month'] = tx['event_time'].dt.to_period('M')
g = tx.groupby('customer_id')
beh = pd.DataFrame({
    'tx_count': g.size(),
    'months': g['month'].nunique(),
    'amt_mean': g['amount'].mean(),
    'amt_std': g['amount'].std().fillna(0.0),
    'amt_p95': g['amount'].quantile(0.95)
}).fillna(0.0)
beh['tx_per_month'] = beh['tx_count'] / beh['months'].replace(0, np.nan)
beh['tx_per_month'] = beh['tx_per_month'].fillna(0.0)

# Normalize channel names and compute online share
tx['channel'] = tx['channel'].astype(str).str.lower().map({
    'online':'online','ecom':'online','e-commerce':'online','app':'online','web':'online',
    'pos':'pos','in-store':'pos','instore':'pos','store':'pos'
}).fillna('pos')
chan = tx.pivot_table(index='customer_id', columns='channel', values='amount', aggfunc='sum', fill_value=0.0)
for c in ['online','pos']:
    if c not in chan.columns: chan[c] = 0.0
chan['online_share'] = chan['online'] / (chan['online'] + chan['pos']).replace(0, np.nan)
chan['online_share'] = chan['online_share'].fillna(0.0)

# Diversity
div = g.agg(merchant_n=('merchant','nunique'), cat_n=('cat','nunique'))
div['merchant_diversity'] = div['merchant_n'] / beh['tx_count'].replace(0, 1)
div['cat_diversity'] = div['cat_n'] / beh['tx_count'].replace(0, 1)

# Join all
feat = pivot.drop(columns=['total_spend']).join([
    beh[['tx_count','tx_per_month','amt_mean','amt_std','amt_p95']],
    chan[['online_share']],
    div[['merchant_diversity','cat_diversity']]
], how='left').fillna(0.0)

ucf = ucf.rename(columns={'user':'customer_id'})
feat = feat.join(ucf.set_index('customer_id')[['n_cards','avg_credit_limit','has_credit_card']], how='left').fillna(0.0)

feat.reset_index().to_csv("customer_features_altman.csv", index=False)
print("Wrote customer_features_altman.csv", feat.shape)
