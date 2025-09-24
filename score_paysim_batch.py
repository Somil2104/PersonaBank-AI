import sys, json, numpy as np, xgboost as xgb

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

def score_stream(fin, fout):
    for line in fin:
        if not line.strip():
            continue
        row = json.loads(line)
        X = transform_row(row)
        d = xgb.DMatrix(X, feature_names=FEATURES)
        p = float(bst.predict(d)[0])
        row['_prob'] = p
        row['_decision'] = int(p >= THRESH)
        fout.write(json.dumps(row) + "\n")

if __name__ == "__main__":
    fin = open(sys.argv[1], 'r') if len(sys.argv) > 1 else sys.stdin
    fout = open(sys.argv[2], 'w') if len(sys.argv) > 2 else sys.stdout
    score_stream(fin, fout)
    if fin is not sys.stdin: fin.close()
    if fout is not sys.stdout: fout.close()
