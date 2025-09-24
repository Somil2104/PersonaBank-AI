import pandas as pd
import xgboost as xgb
from sklearn.metrics import average_precision_score, roc_auc_score

train = pd.read_csv('paysim_train.csv')
test  = pd.read_csv('paysim_test.csv')

y_tr = train['isfraud'].values
y_te = test['isfraud'].values
X_cols = [c for c in train.columns if c not in ['isfraud','step']]

dtr = xgb.DMatrix(train[X_cols], label=y_tr, nthread=-1)
dte = xgb.DMatrix(test[X_cols],  label=y_te, nthread=-1)

scale_pos_weight = (len(y_tr) - y_tr.sum()) / max(1, y_tr.sum())

params = {
    'objective': 'binary:logistic',
    'eval_metric': ['auc','aucpr'],
    'tree_method': 'hist',
    'eta': 0.1,
    'max_depth': 6,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'scale_pos_weight': float(scale_pos_weight),
}
bst = xgb.train(params, dtr, num_boost_round=300, evals=[(dtr,'train')], verbose_eval=50)

probs = bst.predict(dte)
print("ROC-AUC:", roc_auc_score(y_te, probs))
print("PR-AUC:", average_precision_score(y_te, probs))
