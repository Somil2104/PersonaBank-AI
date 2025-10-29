import pandas as pd

users_p = "sd254_users.csv"
cards_p = "sd254_cards.csv"
tx_p    = "User0_credit_card_transactions.csv"  # change if your filename differs

# Load users
users = pd.read_csv(users_p)
users.columns = [c.strip().lower().replace(' ', '_') for c in users.columns]
if 'user' not in users.columns and 'person' in users.columns:
    users = users.rename(columns={'person':'user'})
users['user'] = users['user'].astype(str)

# Load cards
cards = pd.read_csv(cards_p)
cards.columns = [c.strip().lower().replace(' ', '_') for c in cards.columns]
cards['user'] = cards['user'].astype(str)
cards['credit_limit'] = (cards['credit_limit'].astype(str)
    .str.replace('[^0-9.-]','', regex=True).replace('', '0').astype(float))

user_card_agg = cards.groupby('user').agg(
    n_cards=('card_number','count'),
    avg_credit_limit=('credit_limit','mean'),
    has_credit_card=('card_type', lambda s: int(any('credit' in str(x).lower() for x in s)))
).reset_index()

# Load transactions
tx = pd.read_csv(tx_p, low_memory=False)
tx.columns = [c.strip().lower().replace(' ', '_') for c in tx.columns]
tx['user'] = tx['user'].astype(str)
tx['amount'] = (tx['amount'].astype(str)
                .str.replace('[^0-9.-]','', regex=True)
                .replace('', '0').astype(float))

# Compose event_time from Y/M/D + Time
dt = pd.to_datetime(
    tx['year'].astype(int).astype(str) + '-' +
    tx['month'].astype(int).astype(str).str.zfill(2) + '-' +
    tx['day'].astype(int).astype(str).str.zfill(2) + ' ' +
    tx['time'].astype(str), errors='coerce'
)
tx['event_time'] = pd.to_datetime(dt, utc=True)

# Channel from use_chip
use_chip = tx['use_chip'].astype(str).str.lower()
tx['channel'] = 'pos'
tx.loc[use_chip.str.contains('online'), 'channel'] = 'online'

tx = tx.rename(columns={'merchant_name':'merchant', 'mcc':'mcc',
                        'merchant_city':'city','merchant_state':'state'})

# Canonical columns
keep = ['user','event_time','amount','merchant','mcc','city','state','zip','channel']
for k in keep:
    if k not in tx.columns: tx[k] = None

canon = tx[keep].copy()
canon = canon.dropna(subset=['user','event_time','amount'])
canon = canon[canon['amount'] > 0]
canon = canon.rename(columns={'user':'customer_id'})
canon['source'] = 'altman'

canon.to_csv("transactions_unified_altman.csv", index=False)
user_card_agg.to_csv("user_card_features.csv", index=False)
print("Wrote transactions_unified_altman.csv:", len(canon))
print("Wrote user_card_features.csv:", len(user_card_agg))
