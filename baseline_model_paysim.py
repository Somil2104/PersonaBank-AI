import os, json, time
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (
    average_precision_score, roc_auc_score, precision_recall_curve, confusion_matrix
)

# 0) Load data
train = pd.read_csv('paysim_train.csv')
test  = pd.read_csv('paysim_test.csv')

y_tr = train['isfraud'].values
y_te = test['isfraud'].values
X_cols = [c for c in train.columns if c not in ['isfraud','step']]

# Optional: create a small validation from the tail of train (time-aware split inside train)
# Here we use last 10% of train as valid
split_idx = int(len(train) * 0.9)
train_tr = train.iloc[:split_idx]
train_va = train.iloc[split_idx:]

y_tr2 = train_tr['isfraud'].values
y_va  = train_va['isfraud'].values

dtr = xgb.DMatrix(train_tr[X_cols], label=y_tr2, nthread=-1, feature_names=X_cols)
dva = xgb.DMatrix(train_va[X_cols],  label=y_va,  nthread=-1, feature_names=X_cols)
dte = xgb.DMatrix(test[X_cols],      label=y_te,  nthread=-1, feature_names=X_cols)

# 1) Class imbalance handling
pos = y_tr.sum()
scale_pos_weight = (len(y_tr) - pos) / max(1, pos)

# 2) Parameters with regularization and early stopping
params = {
    'objective': 'binary:logistic',
    'eval_metric': ['auc','aucpr'],
    'tree_method': 'hist',
    'eta': 0.08,
    'max_depth': 6,
    'min_child_weight': 5,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'reg_alpha': 0.0,
    'reg_lambda': 1.0,
    'scale_pos_weight': float(scale_pos_weight),
}

evals = [(dtr, 'train'), (dva, 'valid')]
bst = xgb.train(
    params,
    dtr,
    num_boost_round=1000,
    evals=evals,
    early_stopping_rounds=50,
    verbose_eval=50
)

# 3) Evaluate on test
probs = bst.predict(dte, iteration_range=(0, bst.best_iteration+1))
roc = roc_auc_score(y_te, probs)
pr_auc = average_precision_score(y_te, probs)
print("ROC-AUC:", roc)
print("PR-AUC:", pr_auc)

# 4) Threshold tuning toward target precision
prec, rec, thr = precision_recall_curve(y_te, probs)
target_precision = 0.95
mask = prec >= target_precision
if mask.any():
    idx = np.argmax(rec[mask])
    thr_sel = thr[np.where(mask)[0][idx]-1] if np.where(mask)[0][idx] > 0 else 0.5
    prec_sel = float(prec[np.where(mask)[0][idx]])
    rec_sel  = float(rec[np.where(mask)[0][idx]])
else:
    f1 = 2 * (prec * rec) / np.maximum(prec + rec, 1e-9)
    idx = int(np.argmax(f1[:-1]))
    thr_sel = float(thr[idx])
    prec_sel = float(prec[idx])
    rec_sel  = float(rec[idx])

preds = (probs >= thr_sel).astype(int)
tn, fp, fn, tp = confusion_matrix(y_te, preds).ravel()
print("Selected threshold:", thr_sel)
print("Confusion Matrix (tn, fp, fn, tp):", tn, fp, fn, tp)
print("Precision:", (tp/(tp+fp)) if (tp+fp)>0 else 0.0)
print("Recall:", (tp/(tp+fn)) if (tp+fn)>0 else 0.0)

# 5) Save artifacts (model + metadata)
bst.save_model('paysim_xgb.json')
meta = {
    "model": "xgboost",
    "features": X_cols,
    "split_step": 400,
    "best_iteration": int(bst.best_iteration if bst.best_iteration is not None else len(bst.get_dump())-1),
    "threshold": float(thr_sel),
    "trained_at": time.strftime('%Y-%m-%d %H:%M:%S'),
    "metrics": {
        "roc_auc": float(roc),
        "pr_auc": float(pr_auc),
        "precision_at_threshold": float(prec_sel),
        "recall_at_threshold": float(rec_sel),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)
    },
    "params": params
}
with open('paysim_xgb_meta.json', 'w') as f:
    json.dump(meta, f, indent=2)
print("Saved paysim_xgb.json and paysim_xgb_meta.json")
