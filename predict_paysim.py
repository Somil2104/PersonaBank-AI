import json, numpy as np, xgboost as xgb

# Load artifacts
bst = xgb.Booster()
bst.load_model('paysim_xgb.json')
with open('paysim_xgb_meta.json') as f:
    meta = json.load(f)
FEATURES = meta['features']
THRESH = meta['threshold']

def transform_row(row):
    out = {
        'amount': row.get('amount', 0.0),
        'amount_to_oldbalanceorg': (row['amount'] / row['oldbalanceorg']) if row.get('oldbalanceorg') else 0.0,
        'amount_to_oldbalancedest': (row['amount'] / row['oldbalancedest']) if row.get('oldbalancedest') else 0.0,
        'delta_origin': row.get('newbalanceorig', 0.0) - row.get('oldbalanceorg', 0.0),
        'delta_dest': row.get('newbalancedest', 0.0) - row.get('oldbalancedest', 0.0),
        'type_CASH_IN':   1 if row.get('type') == 'CASH_IN' else 0,
        'type_CASH_OUT':  1 if row.get('type') == 'CASH_OUT' else 0,
        'type_DEBIT':     1 if row.get('type') == 'DEBIT' else 0,
        'type_PAYMENT':   1 if row.get('type') == 'PAYMENT' else 0,
        'type_TRANSFER':  1 if row.get('type') == 'TRANSFER' else 0,
    }
    return np.array([out.get(c, 0.0) for c in FEATURES], dtype=float).reshape(1, -1)

def predict_one(row):
    X = transform_row(row)
    d = xgb.DMatrix(X, feature_names=FEATURES)
    p = float(bst.predict(d)[0])
    return {"probability": p, "decision": int(p >= THRESH)}

if __name__ == "__main__":
    example = {
        "amount": 200000.0,
        "oldbalanceorg": 200000.0,
        "newbalanceorig": 0.0,
        "oldbalancedest": 500.0,
        "newbalancedest": 200500.0,
        "type": "CASH_OUT"
    }


    print(predict_one(example))
