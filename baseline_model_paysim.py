import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.linear_model import LogisticRegression

train = pd.read_parquet('data/processed/paysim_train.parquet')
test  = pd.read_parquet('data/processed/paysim_test.parquet')

features = [c for c in train.columns if c not in ['isfraud','step']]
Xtr, ytr = train[features], train['isfraud']
Xte, yte = test[features],  test['isfraud']

clf = LogisticRegression(max_iter=1000, n_jobs=-1)
clf.fit(Xtr, ytr)

probs = clf.predict_proba(Xte)[:,1]
print("ROC-AUC:", roc_auc_score(yte, probs))
print("PR-AUC:", average_precision_score(yte, probs))
