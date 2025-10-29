import pandas as pd
from datetime import datetime, timedelta, timezone
rows, base = [], datetime(2024, 9, 1, tzinfo=timezone.utc)

def add(user, start_day, mcc, amt, merchant, city, state, channel='pos', n=10, step=1):
    for i in range(n):
        t = base + timedelta(days=start_day + i*step)
        rows.append({
            'customer_id': user,
            'event_time': t.isoformat(),
            'amount': float(amt),
            'merchant': merchant,
            'mcc': str(mcc),
            'city': city,
            'state': state,
            'zip': '00000',
            'channel': channel,
            'source': 'demo'
        })

# U0: Everyday Groceries/Dining (high freq, small ticket)
add(0, 0, 5411, 30, 'GROCERY-MART', 'A', 'CA', 'pos', n=24, step=1)
add(0, 0, 5812, 18, 'CAFE-CO', 'A', 'CA', 'pos', n=12, step=2)

# U1: Traveler High-Value (low freq, big ticket, online)
add(1, 0, 3000, 600, 'AIRLINE-ABC', 'B', 'NY', 'online', n=2, step=15)
add(1, 3, 4112, 150, 'RAIL-LINE', 'B', 'NY', 'pos', n=2, step=20)

# U2: Online Retail/Apparel (mid freq, mid ticket, online-heavy)
add(2, 0, 5651, 90, 'APPAREL-CO', 'C', 'TX', 'online', n=10, step=3)
add(2, 0, 5999, 60, 'ONLINE-RETAIL', 'C', 'TX', 'online', n=8, step=4)

# U3: Utilities/Bills (steady freq, low ticket)
add(3, 0, 4812, 50, 'TELCO', 'D', 'WA', 'online', n=6, step=5)
add(3, 1, 4899, 70, 'ISP', 'D', 'WA', 'online', n=6, step=5)

# U4: Occasional Big Spender (very low freq, high ticket POS)
add(4, 0, 5999, 800, 'ELECTRONICS-STORE', 'E', 'IL', 'pos', n=1)
add(4, 20, 5651, 450, 'LUXURY-APPAREL', 'E', 'IL', 'pos', n=1)

pd.DataFrame(rows).to_csv("transactions_unified_altman.csv", index=False)
print("Wrote demo transactions_unified_altman.csv with", len(rows), "rows and 5 users")
