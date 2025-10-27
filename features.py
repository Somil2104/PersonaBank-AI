def transform_transaction(row):
    amt = float(row.get('amount', 0.0) or 0.0)
    obo = float(row.get('oldbalanceorg', 0.0) or 0.0)
    obd = float(row.get('oldbalancedest', 0.0) or 0.0)
    nbo = float(row.get('newbalanceorig', 0.0) or 0.0)
    nbd = float(row.get('newbalancedest', 0.0) or 0.0)
    t = row.get('type')
    return {
        'amount': amt,
        'amount_to_oldbalanceorg': (amt / obo) if obo else 0.0,
        'amount_to_oldbalancedest': (amt / obd) if obd else 0.0,
        'delta_origin': nbo - obo,
        'delta_dest': nbd - obd,
        'type_CASH_IN':   1 if t == 'CASH_IN' else 0,
        'type_CASH_OUT':  1 if t == 'CASH_OUT' else 0,
        'type_DEBIT':     1 if t == 'DEBIT' else 0,
        'type_PAYMENT':   1 if t == 'PAYMENT' else 0,
        'type_TRANSFER':  1 if t == 'TRANSFER' else 0,
    }
